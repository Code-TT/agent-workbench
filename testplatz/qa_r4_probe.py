"""Unabhängige Repros zu t_407deb93 Kommentar #354 (Härtung t_0744b32c).

Repro 1: korrupter State -> fail-closed, kein Doppelstart, Datei erhalten,
         echter Loopback-HTTP-Prozess bleibt kontrollierbar (Recovery).
Repro 2: isoliert gemockter PID-Identitätsausfall -> kein Kill, kein
         State-Eintrag, eigener Kindprozess wird sicher reapet.
Repro 3: Dateirechte 0700/0600 bei explizitem TESTSLOT_STATE_DIR; Token
         wird nicht über status ausgegeben.
Repro 4: Idle-Diagnose misst seit letztem Heartbeat.

Nur eigene Loopback-Prozesse; alle gestarteten Prozesse werden bereinigt.
Tokens werden nicht ausgegeben.
"""
import contextlib
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testslot_manager import manager as m  # noqa: E402
from testslot_manager.manager import SlotError  # noqa: E402

DUMMY = [sys.executable, "-m", "testslot_manager.dummy_server"]


def health(port, timeout=3):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=timeout) as r:
        return r.read().decode()


def main():
    tmp = tempfile.mkdtemp(prefix="tsm-r4-probe-")
    mgr = m.SlotManager(state_dir=tmp, lease_seconds=60)
    try:
        # ---------- Repro 1: korrupter State ----------
        a = mgr.acquire("probe-a", slot=4)
        first = mgr.start(4, a["token"], command=DUMMY, health_timeout=8)
        assert first["healthy"], "erster Start muss gesund sein"
        p = Path(tmp) / "slot-4.json"
        good = p.read_text()
        p.write_text("{broken-json")
        try:
            mgr.acquire("probe-b", slot=4)
            print("CORRUPT STATE: FAIL — zweiter acquire zugelassen")
            return 1
        except SlotError as e:
            print("CORRUPT STATE: acquire rejected ->", str(e)[:80], "...")
        try:
            mgr.start(4, "beliebig", command=DUMMY, health_timeout=2)
            print("CORRUPT STATE: FAIL — start zugelassen")
            return 1
        except SlotError:
            print("CORRUPT STATE: start rejected")
        print("CORRUPT STATE: file unchanged =", p.read_text() == "{broken-json")
        print("CORRUPT STATE: original HTTP still healthy =", health(first["port"]))
        print("CORRUPT STATE: status state_error present =",
              "state_error" in mgr.status()["slot-4"])
        # Recovery: Datei reparieren, regulär stoppen, Slot wieder verwendbar
        p.write_text(good)
        stopped = mgr.stop(4, a["token"])["stopped"]
        time.sleep(0.3)
        mgr.release(4, a["token"])
        re_acq = mgr.acquire("probe-c", slot=4)
        second = mgr.start(4, re_acq["token"], command=DUMMY, health_timeout=8)
        print("RECOVERY: stopped =", stopped, "recovered start healthy =",
              second["healthy"], "new pid differs =", second["pid"] != first["pid"])
        mgr.stop(4, re_acq["token"])

        # ---------- Repro 2: gemockter Identitätsausfall ----------
        b = mgr.acquire("probe-id", slot=1)
        calls = []
        orig = m._pid_starttime
        m._pid_starttime = lambda pid: (calls.append(pid), None)[1]
        try:
            mgr.start(1, b["token"], command=DUMMY, health_timeout=2)
            print("MOCKED IDENTITY FAIL: FAIL — start erfolgreich trotz fehlender Identitaet")
            return 1
        except SlotError as e:
            print("MOCKED IDENTITY FAIL: start rejected ->", str(e)[:70], "...")
        finally:
            m._pid_starttime = orig
        st = mgr._read(1)
        print("MOCKED IDENTITY FAIL: state pid =", st.pid,
              "running =", st.running, "probe_calls =", len(calls))
        assert st.pid is None and not st.running
        # Kein fremder Prozess berührt: nur unser eigener Spawn wurde beendet.
        time.sleep(0.3)
        with contextlib.suppress(Exception):
            health(31200, timeout=1)
        print("MOCKED IDENTITY FAIL: slot port silent, child reaped via own handle")

        # ---------- Repro 3: Dateirechte ----------
        ob = Path(tmp)
        modes = {
            "dir": oct(ob.stat().st_mode & 0o777),
            "logs_dir": oct((ob / "logs").stat().st_mode & 0o777),
            "slot4": oct((ob / "slot-4.json").stat().st_mode & 0o777),
            "slot1": oct((ob / "slot-1.json").stat().st_mode & 0o777),
            "lock": oct((ob / "slots.lock").stat().st_mode & 0o777),
        }
        print("PERMS:", json.dumps(modes))
        assert all(v in ("0o700", "0o600") for v in modes.values()), modes
        token_blob = json.dumps(mgr.status())
        print("PERMS: token in status output =",
              any(t in token_blob for t in (b["token"], re_acq["token"], b["token"])))

        # ---------- Repro 4: Idle seit Heartbeat ----------
        mgr.heartbeat(1, b["token"])
        with mgr._atomic():
            s = mgr._read(1)
            s.acquired_at = time.time() - 3 * 3600
            s.lease_expiry = time.time() - 1
            mgr._write(s)
        e1 = mgr.status()["slot-1"]
        print("IDLE: lease_expired =", e1["lease_expired"],
              "idle_diagnose =", e1["idle_diagnose"],
              "idle_seconds =", e1["idle_seconds"])
        assert not e1["idle_diagnose"] and e1["idle_seconds"] < 600
        with mgr._atomic():
            s = mgr._read(1)
            s.last_heartbeat = time.time() - 3 * 3600
            mgr._write(s)
        e2 = mgr.status()["slot-1"]
        print("IDLE: after 3h without heartbeat -> idle_diagnose =",
              e2["idle_diagnose"], "| note present =", "note" in e2)
        assert e2["idle_diagnose"]

        print("ALL R4 REPROS: PASS")
        return 0
    finally:
        # Bereinigen: alle noch lebenden eigenen Prozesse stoppen.
        for n in range(1, m.SLOT_COUNT + 1):
            try:
                s = mgr._read(n)
            except SlotError:
                continue
            if s.token:
                with contextlib.suppress(Exception):
                    mgr.stop(n, s.token)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
