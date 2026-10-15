# Testplatz-Manager (`testslot_manager`)

Anbieterneutraler CLI-Manager für **vier logische Testplätze** (Slots). Python-stdlib-only,
keine echten npm/DB/Cloud-Aktionen, keine Docker/Supabase-Abhängigkeit. Internes
Infrastruktur-Werkzeug (Kanban `t_407deb93`), kein Produktfeature; soll später in einen
festgelegten Infrastruktur-Repository-Scope übernommen werden.

## CLI

```bash
python3 -m testslot_manager acquire --owner <name> [--slot 1..4]   # -> JSON mit token
python3 -m testslot_manager status
python3 -m testslot_manager heartbeat --slot N --token T           # Lease verlängern
python3 -m testslot_manager start --slot N --token T [--port P] [--health-timeout 30] \
        [-- <eigenes Kommando ...>]                                # Default: Dummy-HTTP-Server
python3 -m testslot_manager restart --slot N --token T [--attempts 2]
python3 -m testslot_manager logs --slot N [--tail 50]
python3 -m testslot_manager stop --slot N --token T
python3 -m testslot_manager release --slot N --token T [--keep-process]
python3 -m testslot_manager db-refresh   # -> hart "nicht verfügbar" (keine Credentials)
python3 -m testslot_manager db-backup    # -> hart "nicht verfügbar" (keine Credentials)
```

## Semantik / Garantien

- **Atomare Slot-Vergabe:** `flock` über alle Vergabe-Entscheidungen; bei 4 belegten
  Slots wird der 5. `acquire` abgewiesen.
- **Ownership-Token (uuid4):** `heartbeat/release/start/restart/stop` verlangen ihn;
  fremde Tokens werden abgelehnt.
- **Lease:** Default 900 s, via `heartbeat` verlängerbar. Abgelaufene Leases sind
  re-acquirierbar; **es wird dabei nichts gelöscht** — Logs/Artefakte bleiben, ein noch
  laufender Prozess wird nicht getötet, sondern als `orphan` vermerkt.
- **Ports:** feste Bereiche — Slot 1: 31200–31219, Slot 2: 31220–31239,
  Slot 3: 31240–31259, Slot 4: 31260–31279 (loopback only).
- **Doppelstartschutz:** `start` auf laufendem Slot → Fehler.
- **Healthcheck-Timeout:** `start` wartet bounded (Default 30 s) auf
  `GET /health = 200`; bei Timeout kontrolliertes Cleanup **ausschließlich des eigenen
  Prozesses** (PID + Startzeit-Prüfung gegen PID-Recycling), Slot bleibt beim Besitzer.
- **Bounded restart:** Default 2 Versuche, dann Endzustand mit Fehlern melden.
- **Idle-Diagnose:** nach 2 h ohne Herzschlag meldet `status` `idle_diagnose: true`
  mit Hinweis — rein informativ, **keine** Löschung, kein Auto-Release, keine Cloud-API.
- **DB-Adapter:** `db-refresh`/`db-backup` existieren, sind aber **bewusst ohne
  Credentials nicht verfügbar** und werfen hart einen Fehler (keine Erfolgssimulation).

## Tests

```bash
python3 -m unittest discover -s tests -v   # 10 Tests, u. a. konkurrierende Vergabe
```

Integrationstests starten einen realen Dummy-HTTP-Server auf loopback und fragen ihn
per HTTP ab. Kein npm, kein Supabase, kein Docker.

## Grenzen (bewusst)

- Kein VPS-Deployment, keine Cloud-Aktionen, kein Supabase-Start — nur loopback-Prozesse.
- `db-refresh`/`db-backup` nicht verfügbar (Zugänge zur externen Dev-Supabase ungeklärt).
- Keine Secrets: der Manager sammelt/protokolliert keine Credentials.
- State liegt unter `~/.testslot-manager/` (überschreibbar via `TESTSLOT_STATE_DIR`).

## Rollback

Der Manager ändert nichts außerhalb seines State-Dirs. Rollback: laufende Slots
`stop`/`release`, dann `rm -rf ~/.testslot-manager` (enthält nur State + Logs).
Keine Installations-Spuren, keine systemweiten Änderungen.
