"""Kern: Slot-Verwaltung mit atomarer Vergabe, Ownership-Token, Lease, Prozessstart.

Designentscheidungen (bewusst, für die spätere Übernahme in ein Infra-Repo):
- Zustand liegt pro Slot als JSON unter <state_dir>/slot-<n>.json; Vergabe wird
  über fcntl.flock auf <state_dir>/slots.lock atomar serialisiert.
- Ownership-Token (uuid4) wird beim acquire erzeugt; schreibende Operationen
  (release/heartbeat/start/restart/stop) verlangen ihn → kein Fremd-Release.
- Lease: acquire/heartbeat setzen expiry = now + lease_seconds. Ein abgelaufener
  Lease kann von anderen re-acquired werden; **es wird nichts gelöscht** — der
  alte Besitzer verliert nur die Zuordnung, Dateien/Logs bleiben erhalten.
- Ports: feste Bereiche, Slot n belegt PORT_BASE + 20*(n-1) .. +19.
- Doppelstartschutz: start auf Slot mit laufendem PID → Fehler.
- Cleanup tötet ausschließlich die vom Manager selbst gestarteten PIDs (wir
  merken uns pid + startzeit; fremde PID-Recycling-Erkennung über starttime).
- Healthcheck-Timeout: start wartet bounded auf HTTP-Bereitschaft; bei Timeout
  kontrolliertes Cleanup des eigenen Prozesses, Slot bleibt frei für Neuversuch.
- Idle-Diagnose: nach 2h ohne Heartbeat meldet status "idle-long" — rein
  informativ, es wird nichts gelöscht oder freigegeben.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

SLOT_COUNT = 4
PORT_BASE = 31200
PORTS_PER_SLOT = 20
IDLE_DIAGNOSE_SECONDS = 2 * 60 * 60  # 2h: nur Diagnose, keine Aktion


class SlotError(Exception):
    """Abgelehnte Operation (belegt, fremder Owner, kein Start etc.)."""


def slot_port_range(n: int) -> tuple[int, int]:
    lo = PORT_BASE + PORTS_PER_SLOT * (n - 1)
    return lo, lo + PORTS_PER_SLOT - 1


@dataclass
class SlotState:
    slot: int
    owner: str | None = None
    token: str | None = None
    acquired_at: float | None = None
    lease_expiry: float | None = None
    pid: int | None = None
    pid_starttime: float | None = None
    port: int | None = None
    log_path: str | None = None
    running: bool = False
    last_error: str | None = None
    start_gen: int = 0  # Startgeneration: schützt gegen veraltete Operationen
    last_heartbeat: float | None = None  # Basis für Idle-Diagnose (2h-Regel)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, text: str) -> "SlotState":
        data = json.loads(text)
        known = cls.__dataclass_fields__
        return cls(**{k: v for k, v in data.items() if k in known})


def _pid_starttime(pid: int) -> float | None:
    """Linux/macOS-agnostisch: Startzeit für Recycling-Erkennung.

    macOS: ps -o lstart als Unix-Timestamp (epoch_seconds); Linux: field 22
    von /proc/<pid>/stat in clock ticks. Rückgabe ist plattformspezifisch, aber
    konsistent vergleichbar innerhalb derselben Maschine.
    """
    try:
        if Path(f"/proc/{pid}/stat").exists():
            parts = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[-1].split()
            return float(parts[19])  # starttime (field 22, 0-indexed nach ')')
        out = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True, text=True,
        )
        if out.returncode == 0 and out.stdout.strip():
            import datetime
            dt = datetime.datetime.strptime(out.stdout.strip(), "%a %b %d %H:%M:%S %Y")
            return dt.timestamp()
    except Exception:
        pass
    return None


def _alive(pid: int, starttime: float | None) -> bool:
    """Prüft, ob genau dieser Prozess (PID + Startzeit) noch lebt.

    Fail-closed: Ohne bekannte Startzeit kann Identität NICHT nachgewiesen
    werden (PID-Recycling) — dann gilt der Prozess als nicht sicher
    zuzuordnen (False). Kein Kill, keine Übernahme auf dieser Basis.
    """
    if pid is None or pid <= 0 or starttime is None:
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return _pid_starttime(pid) == starttime


class SlotManager:
    def __init__(self, state_dir: str | Path | None = None, lease_seconds: int = 900):
        base = os.environ.get("TESTSLOT_STATE_DIR")
        self.state_dir = Path(state_dir or base or Path.home() / ".testslot-manager")
        # Restriktive Rechte unabhängig vom Pfad (Standard ODER explizit):
        # 0700 für Verzeichnisse, 0600 für State-/Lock-/Log-Dateien — der
        # Ownership-Token liegt im State und darf nicht world-readable sein.
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        with contextlib.suppress(OSError):
            os.chmod(self.state_dir, 0o700)
        self.lock_path = self.state_dir / "slots.lock"
        self.logs_dir = self.state_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True, mode=0o700)
        with contextlib.suppress(OSError):
            os.chmod(self.logs_dir, 0o700)
        self.lease_seconds = lease_seconds
        self._spawned: dict[int, subprocess.Popen] = {}  # pid -> Popen (Reaping)

    # ---------- Low-level State ----------

    @contextlib.contextmanager
    def _atomic(self):
        """Exklusiver Lock über alle Slot-Operationen (atomare Vergabe)."""
        fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            with contextlib.suppress(OSError):
                os.chmod(self.lock_path, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def _state_path(self, slot: int) -> Path:
        if not 1 <= slot <= SLOT_COUNT:
            raise SlotError(f"Slot {slot} existiert nicht (1..{SLOT_COUNT})")
        return self.state_dir / f"slot-{slot}.json"

    def _read(self, slot: int) -> SlotState:
        p = self._state_path(slot)
        if not p.exists():
            return SlotState(slot=slot)
        try:
            text = p.read_text()
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("State ist kein JSON-Objekt")
            return SlotState.from_json(text)
        except SlotError:
            raise
        except Exception as e:
            # Fail-closed: korrupter/unlesbarer State ist KEIN neutraler
            # freier Slot. Kein Doppelstart, keine Vergabe, kein Start —
            # und die Originaldatei wird nicht überschrieben. Recovery:
            # Datei manuell reparieren (Token steht darin) bzw. aus
            # Sicherung wiederherstellen, danach normal stoppen/acquire.
            raise SlotError(
                f"Slot {slot}: State korrupt/unlesbar — fail-closed, "
                f"keine Vergabe/Start (Datei erhalten: {p}): {e}") from e

    def _write(self, state: SlotState) -> None:
        p = self._state_path(slot := state.slot)
        tmp = p.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, state.to_json().encode())
        finally:
            os.close(fd)
        with contextlib.suppress(OSError):
            os.chmod(tmp, 0o600)
        os.replace(tmp, p)  # atomar
        with contextlib.suppress(OSError):
            os.chmod(p, 0o600)

    # ---------- acquire / heartbeat / release ----------

    def acquire(self, owner: str, slot: int | None = None,
                steal: bool = False) -> dict:
        """Belegt einen Slot atomar. Ohne slot-Wunsch: erster freier (oder
        abgelaufener Lease) Slot, sonst SlotError 'alle belegt'.

        Wichtig (Prozesszuordnung): Ist trotz abgelaufenem Lease/Owner=None
        noch ein vom Manager gestarteter Prozess am Leben, wird der Slot
        NICHT neu vergeben — der alte Owner kann mit seinem Token stoppen.
        Nur mit steal=True wird dieser eigene (verwaiste) Prozess kontrolliert
        beendet und der Slot übernommen."""
        with self._atomic():
            candidates = [slot] if slot else range(1, SLOT_COUNT + 1)
            for n in candidates:
                st = self._read(n)
                now = time.time()
                free = st.owner is None or (st.lease_expiry or 0) < now
                if free and st.running and st.pid and st.pid_starttime is None:
                    # Identität der laufenden Zuordnung nicht nachweisbar
                    # (z. B. Legacy-State): fail-closed — kein Kill, keine
                    # Übernahme, kein Doppelstart. Manuelle Reparatur nötig.
                    if slot is None:
                        continue
                    raise SlotError(
                        f"Slot {n}: laufender Prozess pid={st.pid} ohne "
                        "nachweisbare Startzeit — Identitaet ungesichert, "
                        "Uebernahme/Kill abgelehnt (State manuell reparieren)")
                if free and st.running and st.pid and _alive(st.pid, st.pid_starttime):
                    # Laufender Prozess gehört zur bisherigen Zuordnung —
                    # weder löschen noch unkontrolliert neu vergeben.
                    if not steal:
                        if slot is None:
                            # Auto-Vergabe: verwaisten Slot überspringen und
                            # weiter suchen, statt trotz freier Slots abzubrechen.
                            continue
                        raise SlotError(
                            f"Slot {n}: Lease abgelaufen, aber Prozess "
                            f"pid={st.pid} (Port {st.port}) laeuft noch. "
                            "Alter Owner kann mit seinem Token stoppen; "
                            "Uebernahme nur mit acquire --steal.")
                    self._kill_own(st)
                    free = True
                if free:
                    token = uuid.uuid4().hex
                    new = SlotState(
                        slot=n, owner=owner, token=token,
                        acquired_at=now, lease_expiry=now + self.lease_seconds,
                        pid=None, pid_starttime=None, port=None,
                        log_path=st.log_path, running=False,
                        last_error=None,
                    )
                    self._write(new)
                    return {"slot": n, "owner": owner, "token": token,
                            "ports": slot_port_range(n)}
            if slot:
                raise SlotError(f"Slot {slot} ist belegt (aktiver Lease)")
            raise SlotError("alle 4 Slots belegt (5. acquire abgewiesen)")

    def heartbeat(self, slot: int, token: str) -> dict:
        with self._atomic():
            st = self._require_owner(slot, token, "heartbeat")
            st.lease_expiry = time.time() + self.lease_seconds
            st.last_heartbeat = time.time()
            self._write(st)
            return {"slot": slot, "lease_expiry": st.lease_expiry}

    def release(self, slot: int, token: str, stop_process: bool = True) -> dict:
        with self._atomic():
            st = self._require_owner(slot, token, "release")
            if not stop_process and st.running and st.pid \
                    and _alive(st.pid, st.pid_starttime):
                # Prozesszuordnung nicht verlieren: ohne Stop kein Release.
                raise SlotError(
                    f"Slot {slot}: release --keep-process abgelehnt — es laeuft "
                    f"noch ein Prozess (pid={st.pid}). Erst stop, oder release "
                    "ohne --keep-process.")
            stopped = False
            if stop_process and st.running and st.pid:
                stopped = self._kill_own(st)
            self._write(SlotState(slot=slot, last_error=None,
                                  log_path=st.log_path))
            return {"slot": slot, "released": True, "process_stopped": stopped}

    def _require_owner(self, slot: int, token: str, action: str) -> SlotState:
        st = self._read(slot)
        if st.owner is None or st.token is None:
            raise SlotError(f"Slot {slot} ist nicht belegt — {action} abgelehnt")
        if st.token != token:
            raise SlotError(f"Slot {slot}: falscher Owner-Token — {action} abgelehnt")
        return st

    # ---------- start / restart / stop / logs ----------

    def start(self, slot: int, token: str, command: list[str] | None = None,
              port: int | None = None, health_timeout: float = 30.0) -> dict:
        """Startet einen Prozess im Slot. Default-Kommando: Dummy-HTTP-Server.

        Doppelstartschutz, feste Portwahl aus dem Slot-Bereich, bounded
        Healthcheck mit kontrolliertem Cleanup (nur eigener Prozess)."""
        cmd = command or [sys.executable, "-m", "testslot_manager.dummy_server"]
        with self._atomic():
            st = self._require_owner(slot, token, "start")
            if st.running and st.pid and st.pid_starttime is None:
                raise SlotError(
                    f"Slot {slot}: laufende Prozesszuordnung (pid={st.pid}) "
                    "ohne nachweisbare Startzeit — Doppelstartschutz "
                    "fail-closed, State manuell reparieren")
            if st.running and st.pid and _alive(st.pid, st.pid_starttime):
                raise SlotError(f"Slot {slot} laeuft bereits (pid={st.pid}) — Doppelstart abgewiesen")
            lo, hi = slot_port_range(slot)
            if port is None:
                port = self._free_port(lo, hi)
            elif not (lo <= port <= hi):
                raise SlotError(f"Port {port} liegt nicht im Bereich {lo}-{hi} von Slot {slot}")
            else:
                # Expliziter Port: vor Spawn belegt-Prüfung. Sonst könnte die
                # Healthcheck-Antwort von einem FREMDEN Listener auf diesem
                # Port stammen und als eigener gesunder Start missdeutet werden.
                if not self._port_bindable(port):
                    raise SlotError(
                        f"Port {port} ist bereits belegt — start abgelehnt "
                        "(kein fremder Listener als eigener Start akzeptiert)")
            log_path = self.logs_dir / f"slot-{slot}.log"
            env = dict(os.environ, TESTSLOT_PORT=str(port))
            with open(log_path, "ab") as logf:
                proc = subprocess.Popen(
                    cmd, env=env,
                    stdout=logf, stderr=subprocess.STDOUT,
                    start_new_session=True,
            )
            try:
                os.chmod(log_path, 0o600)
            except OSError:
                pass
            self._spawned[proc.pid] = proc
            st.start_gen = getattr(st, "start_gen", 0) + 1
            my_gen = st.start_gen
            t0 = _pid_starttime(proc.pid)
            if t0 is None:
                # Identitätsermittlung fehlgeschlagen: NICHT persistieren
                # (kein pid/starttime-Eintrag, kein gesunder Start möglich),
                # Kind über den EIGENEN Handle sicher beenden/reapen — kein
                # Kill auf unbekannter Grundlage.
                with contextlib.suppress(Exception):
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    proc.wait(timeout=15)
                if proc.poll() is None:
                    with contextlib.suppress(Exception):
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                with contextlib.suppress(Exception):
                    proc.wait(timeout=15)
                self._spawned.pop(proc.pid, None)
                raise SlotError(
                    "Prozessidentitaet (Startzeit) nicht ermittelbar — "
                    "start abgebrochen, kein State-Eintrag, Prozess "
                    "ueber eigenen Handle beendet")
            st.pid = proc.pid
            st.pid_starttime = t0
            st.port = port
            st.log_path = str(log_path)
            st.running = True
            st.last_error = None
            self._write(st)
            my_pid, my_starttime = proc.pid, st.pid_starttime

        # Healthcheck außerhalb des Locks (blockiert keine Vergabe).
        ok, detail = self._wait_healthy(port, health_timeout)
        if ok:
            # Erfolgsweg: Identität gegen zwischenzeitlichen stop/Neuvergabe
            # prüfen (stop derselben Generation ändert Token/Gen NICHT —
            # deshalb zusätzlich pid/starttime/running vergleichen). Ein
            # geänderter/abgebrochener Start wird als solcher gemeldet,
            # nicht als gesunder Erfolg.
            with self._atomic():
                st_now = self._read(slot)
            same = (st_now.token == token and st_now.start_gen == my_gen
                    and st_now.pid == my_pid
                    and st_now.pid_starttime == my_starttime
                    and st_now.running and _alive(my_pid, my_starttime))
            if same:
                return {"slot": slot, "pid": my_pid, "port": port,
                        "healthy": True, "log": st.log_path}
            return {"slot": slot, "pid": my_pid, "port": port,
                    "healthy": False, "log": st.log_path,
                    "warning": ("start nicht als gesunder Erfolg gueltig: "
                                "Slot-State wurde zwischenzeitlich gestoppt/"
                                "geaendert (pid/gen/running-Identitaet "
                                f"verletzt; state_pid={st_now.pid}, "
                                f"gen={st_now.start_gen}, running="
                                f"{st_now.running}) — kein State-Restore")}
        # Timeout: kontrolliertes Cleanup ausschließlich des eigenen Prozesses
        # (unser Spawn, pid+starttime). State nur überschreiben, wenn die
        # Startgeneration unverändert ist — sonst hat ein neuerer Start/stop
        # das Slot übernommen und wir dürfen nichts umschreiben.
        self._kill_own(SlotState(slot=slot, pid=my_pid, pid_starttime=my_starttime))
        with self._atomic():
            st2 = self._read(slot)
            if st2.token == token and st2.start_gen == my_gen and st2.pid == my_pid:
                st2.running = False
                st2.pid = None
                st2.pid_starttime = None
                st2.port = None
                st2.last_error = f"healthcheck timeout nach {health_timeout}s: {detail}"
                self._write(st2)
                raise SlotError(st2.last_error)
            raise SlotError(
                f"healthcheck timeout nach {health_timeout}s: {detail} — "
                f"aber Slot-State inzwischen geaendert (Generation "
                f"{st2.start_gen} != {my_gen}); kein Cleanup geschrieben")

    def _free_port(self, lo: int, hi: int) -> int:
        for p in range(lo, hi + 1):
            if self._port_bindable(p):
                return p
        raise SlotError(f"kein freier Port in {lo}-{hi}")

    @staticmethod
    def _port_bindable(port: int) -> bool:
        """True, wenn sich der Port jetzt binden laesst. SO_REUSEADDR erlaubt
        TIME_WAIT-Restart, lehnt aber einen AKTIV lauschenden Listener ab."""
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return True
            except OSError:
                return False

    @staticmethod
    def _wait_port_free(port: int, timeout: float) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with socket.socket() as s:
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(("127.0.0.1", port))
                    return True
                except OSError:
                    time.sleep(0.2)
        return False

    @staticmethod
    def _wait_healthy(port: int, timeout: float) -> tuple[bool, str]:
        url = f"http://127.0.0.1:{port}/health"
        deadline = time.time() + timeout
        last = ""
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        return True, "ok"
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}"
            except Exception as e:
                last = str(e)
            time.sleep(0.3)
        return False, last or "kein Antwortversuch"

    def _kill_own(self, st: SlotState) -> bool:
        """Beendet NUR den vom Manager gestarteten Prozess (PID+Startzeit).

        Fail-closed: Ohne bekannte Startzeit wird NICHTS signalisiert —
        eine recycelte/fremde PID kann so nie getroffen werden."""
        pid, t0 = st.pid, st.pid_starttime
        if not pid or t0 is None or not _alive(pid, t0):
            return False
        with contextlib.suppress(ProcessLookupError):
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        for _ in range(30):
            if not _alive(pid, t0):
                return True
            time.sleep(0.1)
        with contextlib.suppress(ProcessLookupError):
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        # Kindprozess deterministisch einsammeln (kein ResourceWarning/Zombie):
        proc = self._spawned.pop(pid, None)
        if proc is not None:
            with contextlib.suppress(Exception):
                proc.wait(timeout=15)
        else:
            # Fremde Manager-Instanz: blockierend einsammeln, wenn Kind.
            with contextlib.suppress(ChildProcessError, OSError):
                os.waitpid(pid, 0)
        for _ in range(30):
            if not _alive(pid, t0):
                return True
            time.sleep(0.1)
        return _alive(pid, t0) is False

    def stop(self, slot: int, token: str) -> dict:
        with self._atomic():
            st = self._require_owner(slot, token, "stop")
            stopped = self._kill_own(st)
            st.running = False
            st.pid = None
            st.pid_starttime = None
            st.port = None
            self._write(st)
            return {"slot": slot, "stopped": stopped}

    def restart(self, slot: int, token: str, command: list[str] | None = None,
                max_attempts: int = 2) -> dict:
        """Bounded restart: max. max_attempts Neustarts, dann Endzustand melden."""
        with self._atomic():
            st = self._require_owner(slot, token, "restart")
            prev_port = st.port
            was_running = bool(st.running and st.pid and _alive(st.pid, st.pid_starttime))
            if was_running:
                self._kill_own(st)
                st.running = False
                st.pid = None
                st.pid_starttime = None
                self._write(st)
            # Port-Recycling: bis zu 5s warten, bis der alte Port wieder frei
            # ist, sonst scheitert der 1. Start an "Address already in use".
            if prev_port:
                self._wait_port_free(prev_port, 5.0)
        errors = []
        for attempt in range(1, max_attempts + 1):
            try:
                res = self.start(slot, token, command=command, port=prev_port)
                res["attempts"] = attempt
                return res
            except SlotError as e:
                errors.append(f"Versuch {attempt}: {e}")
        raise SlotError("restart fehlgeschlagen: " + "; ".join(errors))

    def logs(self, slot: int, token: str | None = None, tail: int = 50) -> str:
        """Gibt Log-Tail zurück. Lesen ohne Token erlaubt (read-only)."""
        st = self._read(slot)
        if not st.log_path or not Path(st.log_path).exists():
            return ""
        lines = Path(st.log_path).read_text(errors="replace").splitlines()
        return "\n".join(lines[-tail:])

    # ---------- status / Diagnose ----------

    def status(self) -> dict:
        now = time.time()
        out = {}
        for n in range(1, SLOT_COUNT + 1):
            try:
                st = self._read(n)
            except SlotError as e:
                # Fail-closed sichtbar machen, ohne status() abstürzen zu lassen.
                out[f"slot-{n}"] = {"slot": n, "state_error": str(e)}
                continue
            # Idle-Diagnose misst seit dem LETZTEN Herzschlag (Fallback:
            # acquired_at), nicht seit dem Erwerb. Lease-Ablauf allein genügt
            # nicht; erst 2h ohne Herzschlag + abgelaufener Lease.
            hb_ref = st.last_heartbeat or st.acquired_at
            idle_seconds = int(now - hb_ref) if hb_ref else 0
            entry = {
                "owner": st.owner,
                "running": bool(st.running and st.pid and _alive(st.pid, st.pid_starttime)),
                "pid": st.pid,
                "port": st.port,
                "lease_expired": bool(st.lease_expiry and st.lease_expiry < now),
                "last_heartbeat": st.last_heartbeat,
                "idle_seconds": idle_seconds,
                "idle_diagnose": bool(st.owner and st.lease_expiry
                                      and st.lease_expiry < now
                                      and hb_ref and now - hb_ref >= IDLE_DIAGNOSE_SECONDS),
                "last_error": st.last_error,
            }
            if entry["idle_diagnose"]:
                # Reine Diagnose: Hinweis, KEINE Löschung/Freigabe.
                entry["note"] = ("idle >2h ohne Herzschlag bei abgelaufenem Lease — "
                                 "nur Diagnose; ungesicherte Arbeit wird nicht beruehrt")
            out[f"slot-{n}"] = entry
        return out


# ---------- bewusst NICHT verfügbare Adapter ----------

class DbRefreshUnavailable(Exception):
    pass


class DbBackupUnavailable(Exception):
    pass


def db_refresh(*_a, **_kw):
    """DB-Refresh ist NICHT verfügbar: es liegen keine Credentials vor.
    Keine Erfolgssimulation — bewusst harter Fehler."""
    raise DbRefreshUnavailable(
        "db_refresh nicht verfuegbar: keine DB-Credentials konfiguriert "
        "(externe Dev-Supabase-Zugaenge ungeklaert). Kein Refresh, keine Simulation.")


def db_backup(*_a, **_kw):
    """DB-Backup ist NICHT verfügbar: es liegen keine Credentials vor."""
    raise DbBackupUnavailable(
        "db_backup nicht verfuegbar: keine DB-Credentials konfiguriert.")
