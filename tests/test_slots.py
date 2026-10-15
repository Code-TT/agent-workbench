"""Acceptance-Tests laut Karte:

1. konkurrierende Vergabe: 4 Slots belegt, 5. acquire abgewiesen
2. Owner-Schutz: fremder Token darf release/start/stop nicht
3. Doppelstartschutz
4. restart/stop inkl. real laufendem Dummy-Server
5. Healthcheck-Timeout mit kontrolliertem Cleanup (eigenen Prozess toeten)
6. aktiver Lease verhindert Fremd-acquire; abgelaufener Lease re-acquirierbar
   OHNE Loeschen von Artefakten
7. DB-Adapter melden hart "nicht verfuegbar" (keine Erfolgssimulation)

Der Dummy-Server wird real gestartet und per HTTP abgefragt.
"""
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from testslot_manager import manager as m  # noqa: E402
from testslot_manager.manager import SlotError  # noqa: E402

PKG_DIR = Path(__file__).resolve().parents[1]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mgr = m.SlotManager(state_dir=self.tmp.name, lease_seconds=60)

    def tearDown(self):
        # Aufräumen: alle eigenen Prozesse stoppen, State-Dir wegwerfen.
        for n in range(1, m.SLOT_COUNT + 1):
            st = self.mgr._read(n)
            if st.token:
                try:
                    self.mgr.stop(n, st.token)
                except SlotError:
                    pass
        self.tmp.cleanup()


class TestAcquire(Base):
    def test_konkurrierende_vergabe_4_slots_5ter_abgewiesen(self):
        tokens = []
        for i in range(4):
            res = self.mgr.acquire(f"owner-{i}")
            self.assertEqual(res["slot"], i + 1)
            tokens.append(res["token"])
        with self.assertRaises(SlotError) as cm:
            self.mgr.acquire("owner-5")
        self.assertIn("alle 4 Slots belegt", str(cm.exception))

    def test_slot_wunsch_belegt_abgewiesen(self):
        r1 = self.mgr.acquire("a", slot=2)
        with self.assertRaises(SlotError):
            self.mgr.acquire("b", slot=2)
        self.assertEqual(self.mgr.acquire("b")["slot"], 1)  # niedrigster freier
        del r1

    def test_owner_schutz(self):
        r = self.mgr.acquire("a")
        for fn in (lambda: self.mgr.release(1, "falsch"),
                   lambda: self.mgr.heartbeat(1, "falsch"),
                   lambda: self.mgr.start(1, "falsch"),
                   lambda: self.mgr.stop(1, "falsch")):
            with self.assertRaises(SlotError) as cm:
                fn()
            self.assertIn("falscher Owner-Token", str(cm.exception))
        # korrekter Token funktioniert
        self.mgr.heartbeat(1, r["token"])
        self.mgr.release(1, r["token"])
        st = self.mgr._read(1)
        self.assertIsNone(st.owner)


class TestLease(Base):
    def test_aktiver_lease_verhindert_fremd_acquire(self):
        self.mgr.acquire("a", slot=1)
        with self.assertRaises(SlotError):
            self.mgr.acquire("b", slot=1)

    def test_abgelaufener_lease_reacquirierbar_ohne_loeschen(self):
        r = self.mgr.acquire("a", slot=3)
        log_dir = Path(self.tmp.name) / "logs"
        marker = log_dir / "slot-3.log"
        marker.write_text("ungesicherte arbeit bleibt bestehen\n")
        # Lease künstlich ablaufen lassen
        with self.mgr._atomic():
            st = self.mgr._read(3)
            st.lease_expiry = time.time() - 1
            self.mgr._write(st)
        res = self.mgr.acquire("b", slot=3)
        self.assertEqual(res["owner"], "b")
        self.assertTrue(marker.exists())  # NICHTS geloescht
        # alter Token ist jetzt ungueltig
        with self.assertRaises(SlotError):
            self.mgr.heartbeat(3, r["token"])


class TestProcess(Base):
    def _dummy_cmd(self):
        return [sys.executable, "-m", "testslot_manager.dummy_server"]

    def test_start_healthcheck_stop(self):
        r = self.mgr.acquire("a")
        res = self.mgr.start(1, r["token"], command=self._dummy_cmd())
        self.assertTrue(res["healthy"])
        self.assertTrue(31200 <= res["port"] <= 31219)
        with urllib.request.urlopen(f"http://127.0.0.1:{res['port']}/health", timeout=3) as resp:
            self.assertEqual(resp.read(), b"ok")
        # Doppelstart abgewiesen
        with self.assertRaises(SlotError) as cm:
            self.mgr.start(1, r["token"], command=self._dummy_cmd())
        self.assertIn("Doppelstart", str(cm.exception))
        out = self.mgr.stop(1, r["token"])
        self.assertTrue(out["stopped"])
        time.sleep(0.2)
        with self.assertRaises(Exception):
            urllib.request.urlopen(f"http://127.0.0.1:{res['port']}/health", timeout=1)

    def test_restart_bounded(self):
        r = self.mgr.acquire("a")
        self.mgr.start(1, r["token"], command=self._dummy_cmd())
        res = self.mgr.restart(1, r["token"], command=self._dummy_cmd())
        self.assertEqual(res["attempts"], 1)
        self.assertTrue(res["healthy"])
        self.mgr.stop(1, r["token"])

    def test_healthcheck_timeout_cleanup_nur_eigener_prozess(self):
        r = self.mgr.acquire("a")
        # Kommando, das nie auf /health antwortet, aber unsere PID loggt:
        cmd = [sys.executable, "-c", "import os,time;print(os.getpid(),flush=True);time.sleep(60)"]
        with self.assertRaises(SlotError) as cm:
            self.mgr.start(1, r["token"], command=cmd, health_timeout=1.5)
        self.assertIn("healthcheck timeout", str(cm.exception))
        time.sleep(0.3)
        # Der vom Manager gestartete Prozess wurde kontrolliert beendet:
        log = Path(self.tmp.name) / "logs" / "slot-1.log"
        child_pid = int(log.read_text().strip().splitlines()[0])
        with self.assertRaises(ProcessLookupError):
            os.kill(child_pid, 0)
        st = self.mgr._read(1)
        self.assertFalse(st.running)
        self.assertIn("timeout", st.last_error or "")
        # Slot bleibt beim Besitzer (kein Auto-Release, keine Datenloeschung);
        # nach explizitem Release wieder frei:
        self.mgr.release(1, r["token"], stop_process=False)
        self.assertEqual(self.mgr.acquire("z", slot=1)["slot"], 1)


class TestAdapters(Base):
    def test_db_adapter_hart_nicht_verfuegbar(self):
        with self.assertRaises(m.DbRefreshUnavailable):
            m.db_refresh()
        with self.assertRaises(m.DbBackupUnavailable):
            m.db_backup()


class TestIdleDiagnose(Base):
    def test_idle_nur_diagnose_keine_aktion(self):
        self.mgr.acquire("a", slot=4)
        with self.mgr._atomic():
            st = self.mgr._read(4)
            st.lease_expiry = time.time() - 1
            st.acquired_at = time.time() - 3 * 3600
            self.mgr._write(st)
        status = self.mgr.status()["slot-4"]
        self.assertTrue(status["idle_diagnose"])
        self.assertIn("nicht beruehrt", status["note"])
        self.assertIsNone(status["last_error"])


class TestKonkurrierendEcht(Base):
    """Echter Prozesswettbewerb: 5 parallele CLI-acquire-Prozesse."""

    def test_5_parallele_cli_acquires_4_slots_5ter_abgewiesen(self):
        root = self.tmp.name
        env = dict(os.environ, TESTSLOT_STATE_DIR=root,
                   PYTHONPATH=str(PKG_DIR))

        def cli_acquire(i):
            return subprocess.run(
                [sys.executable, "-m", "testslot_manager",
                 "acquire", "--owner", f"p{i}"],
                env=env, capture_output=True, text=True, cwd=str(PKG_DIR))

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            results = list(ex.map(cli_acquire, range(5)))
        oks = [json.loads(r.stdout) for r in results if r.returncode == 0]
        rejected = [r for r in results if r.returncode != 0]
        self.assertEqual(len(oks), 4)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(sorted(o["slot"] for o in oks), [1, 2, 3, 4])
        self.assertIn("alle 4 Slots belegt", rejected[0].stderr)
        tokens = {o["token"] for o in oks}
        self.assertEqual(len(tokens), 4)  # alle Tokens verschieden


class TestLeaseProzessZuordnung(Base):
    """Regression QA Runde 1: Lease-Wechsel darf Prozesszuordnung nicht verlieren."""

    def _dummy_cmd(self):
        return [sys.executable, "-m", "testslot_manager.dummy_server"]

    def test_abgelaufener_lease_mit_laufendem_prozess_kein_doppelstart(self):
        a = self.mgr.acquire("a", slot=4)
        first = self.mgr.start(4, a["token"], command=self._dummy_cmd(),
                               health_timeout=5)
        # Lease künstlich ablaufen lassen, Prozess läuft weiter
        with self.mgr._atomic():
            st = self.mgr._read(4)
            st.lease_expiry = time.time() - 1
            self.mgr._write(st)
        # zweiter acquire wird abgewiesen — Zuordnung bleibt erhalten
        with self.assertRaises(SlotError) as cm:
            self.mgr.acquire("b", slot=4)
        self.assertIn("laeuft noch", str(cm.exception))
        st = self.mgr._read(4)
        self.assertEqual(st.pid, first["pid"])  # Mapping unveraendert
        self.assertEqual(st.token, a["token"])
        self.assertEqual(st.port, first["port"])
        with urllib.request.urlopen(
                f"http://127.0.0.1:{first['port']}/health", timeout=3) as resp:
            self.assertEqual(resp.read(), b"ok")
        # alter Owner kann weiterhin regulär stoppen
        self.assertTrue(self.mgr.stop(4, a["token"])["stopped"])
        time.sleep(0.2)
        # erst jetzt ist der Slot für einen neuen Owner startbar
        b = self.mgr.acquire("b", slot=4)
        second = self.mgr.start(4, b["token"], command=self._dummy_cmd(),
                                health_timeout=5)
        self.assertNotEqual(second["pid"], first["pid"])
        self.mgr.stop(4, b["token"])

    def test_acquire_steal_beendet_eigenen_verwaisten_prozess(self):
        a = self.mgr.acquire("a", slot=2)
        first = self.mgr.start(2, a["token"], command=self._dummy_cmd(),
                               health_timeout=5)
        with self.mgr._atomic():
            st = self.mgr._read(2)
            st.lease_expiry = time.time() - 1
            self.mgr._write(st)
        b = self.mgr.acquire("b", slot=2, steal=True)
        self.assertEqual(b["slot"], 2)
        time.sleep(0.3)
        with self.assertRaises(Exception):
            urllib.request.urlopen(
                f"http://127.0.0.1:{first['port']}/health", timeout=1)
        second = self.mgr.start(2, b["token"], command=self._dummy_cmd(),
                                health_timeout=5)
        self.assertNotEqual(second["pid"], first["pid"])
        self.mgr.stop(2, b["token"])

    def test_release_keep_process_waehrend_lauf_abgelehnt(self):
        a = self.mgr.acquire("a", slot=1)
        res = self.mgr.start(1, a["token"], command=self._dummy_cmd(),
                             health_timeout=5)
        with self.assertRaises(SlotError) as cm:
            self.mgr.release(1, a["token"], stop_process=False)
        self.assertIn("keep-process abgelehnt", str(cm.exception))
        st = self.mgr._read(1)
        self.assertEqual(st.pid, res["pid"])  # Zuordnung nicht verloren
        self.mgr.stop(1, a["token"])


class TestStaleTimeoutRace(Base):
    """Regression QA Runde 1: alter Healthcheck-Timeout darf neueren Start
    nicht überschreiben (Startgeneration)."""

    def test_alter_timeout_ueberschreibt_neuen_start_nicht(self):
        a = self.mgr.acquire("a", slot=3)
        errors = []

        def slow_start():
            try:
                self.mgr.start(3, a["token"],
                               command=[sys.executable, "-c",
                                        "import time;time.sleep(30)"],
                               health_timeout=1.5)
            except SlotError as e:
                errors.append(str(e))

        t = threading.Thread(target=slow_start)
        t.start()
        for _ in range(100):
            if self.mgr._read(3).running:
                break
            time.sleep(0.01)
        self.mgr.stop(3, a["token"])
        newer = self.mgr.start(3, a["token"],
                               command=[sys.executable,
                                        "-m", "testslot_manager.dummy_server"],
                               port=31259, health_timeout=5)
        saved = self.mgr._read(3)
        try:
            t.join(15)
            self.assertEqual(len(errors), 1)
            self.assertIn("kein Cleanup geschrieben", errors[0])
            # neuerer Start-State ist unangetastet:
            st = self.mgr._read(3)
            self.assertEqual(st.pid, newer["pid"])
            self.assertTrue(st.running)
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{newer['port']}/health",
                    timeout=3) as resp:
                self.assertEqual(resp.read(), b"ok")
        finally:
            self.mgr._kill_own(saved)


class TestCliCustomCommand(Base):
    """Regression QA Runde 1: dokumentiertes `-- <command>` in der CLI."""

    def test_cli_start_mit_eigenem_kommando_nach_doppelstrich(self):
        env = dict(os.environ, TESTSLOT_STATE_DIR=self.tmp.name,
                   PYTHONPATH=str(PKG_DIR))
        base = [sys.executable, "-m", "testslot_manager"]
        r = subprocess.run(base + ["acquire", "--owner", "cli"], env=env,
                           capture_output=True, text=True, cwd=str(PKG_DIR))
        self.assertEqual(r.returncode, 0, r.stderr)
        a = json.loads(r.stdout)
        cmd = base + ["start", "--slot", str(a["slot"]), "--token", a["token"],
                      "--", sys.executable, "-m", "testslot_manager.dummy_server"]
        r = subprocess.run(cmd, env=env, capture_output=True, text=True,
                           cwd=str(PKG_DIR))
        self.assertEqual(r.returncode, 0, r.stderr)
        res = json.loads(r.stdout)
        self.assertTrue(res["healthy"])
        with urllib.request.urlopen(
                f"http://127.0.0.1:{res['port']}/health", timeout=3) as resp:
            self.assertEqual(resp.read(), b"ok")
        r = subprocess.run(base + ["stop", "--slot", str(a["slot"]),
                                   "--token", a["token"]],
                           env=env, capture_output=True, text=True,
                           cwd=str(PKG_DIR))
        self.assertEqual(r.returncode, 0, r.stderr)


class TestRestartBoundedNegativ(Base):
    """Regression QA Runde 1: negative bounded-restart-Auswertung."""

    def test_restart_scheitert_nach_max_attempts_mit_zaehlung(self):
        a = self.mgr.acquire("a", slot=1)
        # nie gesund werdendes Kommando, restart mit 2 Versuchen
        bad = [sys.executable, "-c", "import time;time.sleep(30)"]
        with self.assertRaises(SlotError) as cm:
            self.mgr.restart(1, a["token"], command=bad, max_attempts=2)
        msg = str(cm.exception)
        self.assertIn("Versuch 1", msg)
        self.assertIn("Versuch 2", msg)
        self.assertIn("healthcheck timeout", msg)
        st = self.mgr._read(1)
        self.assertFalse(st.running)  # Endzustand sauber, kein Zombie-State
        self.assertIsNone(st.pid)
        # Owner bleibt, Slot danach regulär startbar:
        res = self.mgr.start(1, a["token"],
                             command=[sys.executable,
                                      "-m", "testslot_manager.dummy_server"],
                             health_timeout=5)
        self.assertTrue(res["healthy"])
        self.mgr.stop(1, a["token"])

    def test_restart_max_attempts_1_nur_ein_versuch(self):
        a = self.mgr.acquire("a", slot=2)
        bad = [sys.executable, "-c", "import time;time.sleep(30)"]
        with self.assertRaises(SlotError) as cm:
            self.mgr.restart(2, a["token"], command=bad, max_attempts=1)
        self.assertIn("Versuch 1", str(cm.exception))
        self.assertNotIn("Versuch 2", str(cm.exception))


class TestIdleAktivLease(Base):
    """Aktiver/verlängerter Lease verhindert Idle-Diagnose trotz Alter."""

    def test_aktiver_lease_verhindert_idle_diagnose_trotz_hohem_alter(self):
        self.mgr.acquire("a", slot=4)
        with self.mgr._atomic():
            st = self.mgr._read(4)
            st.acquired_at = time.time() - 5 * 3600  # sehr alt
            # Lease bleibt aktiv (in Zukunft)
            self.mgr._write(st)
        status = self.mgr.status()["slot-4"]
        self.assertFalse(status["idle_diagnose"])
        self.assertFalse(status["lease_expired"])
        self.assertNotIn("note", status)
        # nach Verlängerung via heartbeat ebenfalls nicht idle:
        r = self.mgr.acquire("b", slot=3)
        self.mgr.heartbeat(3, r["token"])
        self.assertFalse(self.mgr.status()["slot-3"]["idle_diagnose"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
