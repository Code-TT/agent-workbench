"""Tests für das `guard`-Housekeeping (systemd-Timer).

Fail-closed-Garantien:
- aktiver Lease bleibt unangetastet
- abgelaufener Lease wird freigegeben; ein noch laufender Eigenprozess
  wird über PID+Startzeit beendet
- Prozess ohne nachweisbare Startzeit wird NICHT angefasst
- dry_run ändert nichts
- korrupter State wird gemeldet, nicht überschrieben
"""
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from testslot_manager import manager as m  # noqa: E402


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mgr = m.SlotManager(state_dir=self.tmp.name, lease_seconds=900)

    def tearDown(self):
        self.tmp.cleanup()

    def _state(self, slot):
        return self.mgr._read(slot)

    def _expired_running(self, slot, proc):
        self.mgr._write(m.SlotState(
            slot=slot, owner="ghost", token="t",
            acquired_at=time.time() - 2000, lease_expiry=time.time() - 10,
            pid=proc.pid, pid_starttime=m._pid_starttime(proc.pid),
            port=31200 + 20 * (slot - 1), running=True))

    def test_aktiver_lease_unangetastet(self):
        slot = self.mgr.acquire("alice")["slot"]
        res = self.mgr.guard()
        self.assertEqual([a for a in res["actions"] if a["slot"] == slot], [])
        self.assertEqual(self._state(slot).owner, "alice")

    def test_abgelaufener_lease_ohne_prozess_wird_frei(self):
        self.mgr._write(m.SlotState(slot=1, owner="ghost", token="t",
                                    lease_expiry=time.time() - 10))
        self.mgr.guard()
        self.assertIsNone(self._state(1).owner)

    def test_abgelaufener_lease_toter_pid_wird_frei(self):
        self.mgr._write(m.SlotState(slot=2, owner="ghost", token="t",
                                    lease_expiry=time.time() - 10,
                                    pid=999999, pid_starttime=123.0, running=True))
        self.mgr.guard()
        s = self._state(2)
        self.assertIsNone(s.owner)
        self.assertFalse(s.running)

    def test_laufender_prozess_wird_getoetet_nur_mit_startzeit(self):
        proc = subprocess.Popen(["sleep", "60"], start_new_session=True)
        try:
            self._expired_running(3, proc)
            t0 = m._pid_starttime(proc.pid)
            self.mgr.guard()
            self.assertFalse(m._alive(proc.pid, t0), "Eigenprozess muss beendet sein")
            self.assertIsNone(self._state(3).owner)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()

    def test_dry_run_aendert_nichts(self):
        self.mgr._write(m.SlotState(slot=4, owner="ghost", token="t",
                                    lease_expiry=time.time() - 10))
        res = self.mgr.guard(dry_run=True)
        self.assertTrue(res["dry_run"])
        self.assertEqual(self._state(4).owner, "ghost")

    def test_korrupter_state_gemeldet_nicht_ueberschrieben(self):
        p = self.mgr._state_path(1)
        p.write_text("{kaputt")
        res = self.mgr.guard()
        self.assertTrue(any(a["action"] == "state_error" for a in res["actions"]))
        self.assertEqual(p.read_text(), "{kaputt")

    def test_running_ohne_startzeit_wird_nicht_angefasst(self):
        self.mgr._write(m.SlotState(slot=1, owner="ghost", token="t",
                                    lease_expiry=time.time() - 10,
                                    pid=999999, pid_starttime=None, running=True))
        self.mgr.guard()
        self.assertEqual(self._state(1).owner, "ghost")


if __name__ == "__main__":
    unittest.main()
