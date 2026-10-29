# agent-workbench

Werkzeugkasten für die Arbeit mit autonomen Coding-Agenten auf einem
Entwicklungsrechner bzw. Server. Zwei unabhängige Teile:

| Ordner | Zweck |
|---|---|
| [`testplatz/`](testplatz/) | **Testplatz-Manager** — verwaltet knappe Devserver-/Test-Slots für mehrere Agenten, damit sie sich nicht gegenseitig die Maschine zerschießen. |
| [`recovery-tools/`](recovery-tools/) | **Rettungswerkzeuge** — Datenbank-Backup, Restore-Beweis, lokales Dev-Stack-Setup und Skripte zum Bergen verwaister Agenten-Sessions und Worktrees. |

Der Hintergrund: Wenn mehrere Agenten parallel an einem Projekt arbeiten,
startet jeder seinen eigenen `npm run dev`/`next dev`. Auf einem Laptop mit
begrenztem RAM führt das binnen Minuten zum Einfrieren des Systems.
`testplatz/` löst das durch wenige, streng vergebene Slots.
`recovery-tools/` stellt sicher, dass bei einem Datenunfall die
Wiederherstellung nachweisbar funktioniert und verlorene Arbeit wieder
auffindbar ist.

## testplatz/ — Testplatz-Manager

Anbieterneutraler Slot-Manager in reinem Python 3 (Standardbibliothek, keine
Abhängigkeiten).

**Eigenschaften**

- 4 logische Slots, atomare Vergabe über `flock` (keine Race Conditions)
- Ownership-Token (uuid4) — nur der Eigner darf `start`/`stop`/`release`
- Lease (900 s), per `heartbeat` verlängerbar
- feste Portbereiche 31200–31279, ausschließlich auf Loopback
- Doppelstartschutz, Healthcheck mit Timeout
- Startgeneration gegen veraltete Timeouts (killt nie den falschen Prozess)
- tötet **ausschließlich** selbst gestartete Prozesse, erkannt über PID **und**
  Prozess-Startzeit (State fail-closed bei unlesbarem State)

**Benutzung** (aus dem Ordner `testplatz/`)

```bash
python3 -m testslot_manager acquire --owner <name> [--slot 1..4] [--steal]   # -> JSON mit token
python3 -m testslot_manager status
python3 -m testslot_manager heartbeat --slot N --token T                    # Lease verlängern
python3 -m testslot_manager start --slot N --token T [--port P] [--health-timeout 30] -- <kommando>
python3 -m testslot_manager restart --slot N --token T [--attempts 2]
python3 -m testslot_manager logs --slot N [--tail 50]
python3 -m testslot_manager stop --slot N --token T
python3 -m testslot_manager release --slot N --token T [--keep-process]
```

**Tests** (28 Tests, inkl. echter 5-Prozess-Konkurrenz; Laufzeit ~4 min):

```bash
cd testplatz
python3 -m unittest discover -s tests -v
```

**Bekannte Lücken** (ehrlich dokumentiert): `db-refresh` und `db-backup`
antworten hart „nicht verfügbar" — der Supabase-Teil ist nur ein Stub und
liefert bewusst keine Erfolgssimulation. Der echte Devserver-Aufruf ist noch
nicht fest verdrahtet (Default: Dummy-HTTP-Server). Bislang nicht auf einem
Server ausgerollt.

Details: [`testplatz/README.md`](testplatz/README.md)

## recovery-tools/ — Rettungswerkzeuge

| Datei | Zweck |
|---|---|
| `db-backup.sh` | `pg_dump` des Live-Supabase in `~/backups/` |
| `db-restore-test.sh` | wöchentlicher Restore-Beweis (Dump real zurückspielen) |
| `dev-stack-setup.sh` | lokalen Supabase-Stack einrichten |
| `dev-preview.sh` | Preview-Umgebung starten |
| `souls.py`, `write-souls.py.alt` | Agenten-Profile („Souls") lesen/schreiben |
| `inventory-worktrees.py` | Git-Worktrees inventarisieren |
| `harvest_sessions.py` | Agenten-Sessions bergen/auswerten |
| `candidates.py`, `matrix.py`, `replay.py`, `catalog.py` | Kandidaten-/Variantenauswahl, Replay, Katalogbildung |
| `inventory.json`, `inventory.md` | Bestandsaufnahme (Datenbestand als Stand-Dokumentation) |
| `facts/` | kleine Extrakt-Dateien je Projekt |

**Sicherheit:** Alle Skripte lesen Zugangsdaten zur Laufzeit aus einer
externen Datei (`$HOME/.hermes/.env`, überschreibbar via `SUPABASE_ENV_FILE`).
Es sind **keine** Credentials, Schlüssel oder Passwörter im Repo enthalten.

Nicht enthalten (bewusst): `work/`-Scratchdaten (laufzeitabhängige DBs/Logs)
und `*.bak`-Dateien.

## Herkunft

Beide Teile lagen zuvor unversioniert auf dem Entwicklungsrechner und waren
bei einem Aufräumen verloren gegangen. Dieses Repo ist die Sicherung. Die
Historie von `testplatz/` (5 Commits) ist erhalten; `recovery-tools/` kam als
neuer Commit hinzu.

## Lizenz

Noch nicht festgelegt.
