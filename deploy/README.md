# Deployment: Slot-Manager als systemd-Timer (VPS)

Housekeeping analog zum Mac-Cron `dev-slot-guard`: räumt alle 15 Minuten
abgelaufene Leases und verwaiste Slot-Prozesse auf. Es räumt **nur** Prozesse,
die der Manager selbst gestartet hat (Erkennung über PID **und** Startzeit) —
fremde Dienste werden nie angefasst.

## Voraussetzungen

- Python 3 (System-Python genügt, keine Abhängigkeiten)
- Repo-Checkout, z. B. `/srv/agent-workbench`

## Installation

```bash
install -d -m 700 /etc/testplatz /var/lib/testplatz
install -m 644 deploy/slots.conf.example /etc/testplatz/slots.conf
install -m 644 deploy/systemd/testplatz-guard.service /etc/systemd/system/
install -m 644 deploy/systemd/testplatz-guard.timer   /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now testplatz-guard.timer
```

## Prüfen

```bash
systemctl list-timers testplatz-guard.timer
systemctl start testplatz-guard.service          # einmal sofort laufen
journalctl -u testplatz-guard.service -n 30 --no-pager
cd /srv/agent-workbench/testplatz && python3 -m testslot_manager guard --dry-run
```

Leerer `actions`-Array = alles ruhig.

## Tägliche DB-Sicherung

Zusätzlich sichert ein zweiter Timer die Live-DB (04:30) via `db-backup`:

```bash
install -m 644 deploy/systemd/testplatz-db-backup.service /etc/systemd/system/
install -m 644 deploy/systemd/testplatz-db-backup.timer   /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now testplatz-db-backup.timer
```

Voraussetzung: `SUPABASE_DB_URL_LIVE` in `~/.hermes/.env` (Modus 600) und
`docker`. Sichern liegt in `/root/backups/002_EventsPage/` (Dump + Manifest mit
SHA256/Objektzahl, Aufbewahrung 14 Tage, die letzten 3 bleiben immer).

## Konfiguration

| Ort | Zweck |
|---|---|
| `/etc/testplatz/slots.conf` | Slot→Projekt-Zuordnung (informativ) |
| `TESTSLOT_STATE_DIR` (Unit) | Zustandsverzeichnis, Standard `/var/lib/testplatz` |
| `TESTSLOT_POLICY` (Unit) | Pfad zur slots.conf |

Agents müssen denselben `TESTSLOT_STATE_DIR` verwenden wie der Timer, sonst
sehen sie unterschiedliche Slots.
