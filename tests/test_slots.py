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
import json
import os
import subprocess
import sys
import tempfile
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
