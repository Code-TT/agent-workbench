# Testplatz-Manager (`testslot_manager`)

Anbieterneutraler CLI-Manager für **vier logische Testplätze** (Slots). Python-stdlib-only,
keine echten npm/DB/Cloud-Aktionen, keine Docker/Supabase-Abhängigkeit. Internes
Infrastruktur-Werkzeug (Kanban `t_407deb93`), kein Produktfeature; soll später in einen
festgelegten Infrastruktur-Repository-Scope übernommen werden.

## CLI

```bash
python3 -m testslot_manager acquire --owner <name> [--slot 1..4] [--steal]   # -> JSON mit token
python3 -m testslot_manager status
python3 -m testslot_manager heartbeat --slot N --token T           # Lease verlängern
python3 -m testslot_manager start --slot N --token T [--port P] [--health-timeout 30] \
        [-- <eigenes Kommando ...>]                                # Default: Dummy-HTTP-Server
python3 -m testslot_manager restart --slot N --token T [--attempts 2]
python3 -m testslot_manager logs --slot N [--tail 50]
python3 -m testslot_manager stop --slot N --token T
python3 -m testslot_manager release --slot N --token T [--keep-process]
python3 -m testslot_manager db-backup    # echte pg_dump-Sicherung + Manifest (braucht SUPABASE_DB_URL_LIVE + docker)
python3 -m testslot_manager db-refresh   # Pull Live -> Ziel; nur mit TESTSLOT_DEV_DB_URL/DEV_DATABASE_URL
python3 -m testslot_manager guard [--dry-run] [--policy /etc/testplatz/slots.conf]
                                         # Housekeeping: abgelaufene Leases + verwaiste Slot-Prozesse
```

## Semantik / Garantien

- **Atomare Slot-Vergabe:** `flock` über alle Vergabe-Entscheidungen; bei 4 belegten
  Slots wird der 5. `acquire` abgewiesen.
- **Ownership-Token (uuid4):** `heartbeat/release/start/restart/stop` verlangen ihn;
  fremde Tokens werden abgelehnt.
- **Lease:** Default 900 s, via `heartbeat` verlängerbar. Abgelaufene Leases sind
  re-acquirierbar; **es wird dabei nichts gelöscht** — Logs/Artefakte bleiben.
  Läuft trotz abgelaufenem Lease noch ein vom Manager gestarteter Prozess, wird der
  Slot **nicht** neu vergeben (kein Doppelstart, Prozesszuordnung bleibt erhalten):
  der alte Owner kann mit seinem Token `stop`/`release`. Übernahme nur mit
  `acquire --steal`, das genau diesen eigenen (verwaisten) Prozess kontrolliert beendet.
- **Ports:** feste Bereiche — Slot 1: 31200–31219, Slot 2: 31220–31239,
  Slot 3: 31240–31259, Slot 4: 31260–31279 (loopback only).
- **Doppelstartschutz:** `start` auf laufendem Slot → Fehler.
- **`release --keep-process`:** wird abgelehnt, solange ein Prozess läuft — so geht
  keine Prozesszuordnung verloren. Erst `stop`, dann `release`.
- **Healthcheck-Timeout:** `start` wartet bounded (Default 30 s) auf
  `GET /health = 200`; bei Timeout kontrolliertes Cleanup **ausschließlich des eigenen
  Prozesses** (PID + Startzeit-Prüfung gegen PID-Recycling). Jeder `start` erhält eine
  **Startgeneration**: ein veralteter Timeout (oder -Erfolg) überschreibt den State eines
  zwischenzeitlich neueren Starts nicht mehr — der neuere Start bleibt kontrollierbar.
- **`acquire` ohne Slot-Wunsch (Auto-Vergabe):** überspringt verwaiste Slots
  (abgelaufener Lease + lebendiger Prozess) und vergibt den nächsten freien —
  ein verwaister Slot blockiert die Vergabe der übrigen Slots nicht. Expliziter
  `--slot`-Wunsch auf einen verwaisten Slot bleibt abgewiesen (Schutz wie oben).
- **Expliziter Port:** vor dem Prozess-Spawn wird geprüft, ob der Port frei ist
  (SO_REUSEADDR erlaubt TIME_WAIT-Restart, lehnt aktive Listener ab). Ein
  fremder HTTP-Listener auf dem Port kann daher nicht als „gesunder eigener
  Start" missdeutet werden; belegter Port → `start` abgelehnt, ohne Spawn.
- **Erfolgsweg-Validierung:** nach erfolgreichem Healthcheck wird die Identität
  (Token + Startgeneration + PID + `running`) erneut geprüft. Wurde der Start
  zwischenzeitlich `gestoppt` oder neu vergeben, meldet `start` **nicht** still
  `healthy=true`, sondern `healthy=false` mit `warning` — kein State-Restore.
- **Bounded restart:** Default 2 Versuche, dann Endzustand mit gezählten Fehlern
  („Versuch 1 … Versuch 2 …") melden; State endet sauber (`running=false`).
- **Idle-Diagnose:** nach 2 h ohne Herzschlag meldet `status` `idle_diagnose: true`
  mit Hinweis — rein informativ, **keine** Löschung, kein Auto-Release, keine Cloud-API.
- **State fail-closed:** Eine korrupte/unlesbare `slot-<n>.json` ist **kein** neutraler
  freier Slot: `acquire`/`start`/`stop`/`heartbeat` werden mit `SlotError` abgelehnt,
  die Originaldatei wird **nicht überschrieben**, es gibt keinen Doppelstart und keinen
  Datenverlust. `status` zeigt den Slot mit `state_error` statt abzustürzen. Recovery:
  State-Datei manuell reparieren (der Token steht darin) bzw. aus Sicherung
  wiederherstellen, danach regulär `stop`/`acquire`.
- **Prozessidentität (fail-closed):** Ein Kill oder eine Übernahme erfolgt nur mit
  **nachweislicher** PID+Startzeit-Identität. Unbekannte/undefinierbare Startzeit
  (z. B. Legacy-State oder fehlgeschlagene Identitätsermittlung) → **kein Signal,
  keine Zuordnung, keine Übernahme**: `acquire`/`start` auf solche Slots wird
  abgewiesen (Auto-Vergabe überspringt sie). Schlägt die Startzeit-Ermittlung direkt
  nach dem Spawn fehl, persistiert `start` nichts und beendet den soeben gespawnten
  eigenen Kindprozess über den eigenen Popen-Handle — niemals Signale auf
  unbekannter Grundlage (PID-Recycling-Schutz).
- **Idle-Diagnose seit letztem Herzschlag:** `status` misst `idle_seconds` ab
  `last_heartbeat` (Fallback: `acquired_at`); die Diagnose (`idle_diagnose`) greift
  erst bei **2 h ohne Heartbeat** UND abgelaufenem Lease — ein Lease-Ablauf allein
  genügt nicht. Rein informativ, keine Löschung/Aktion.
- **Restriktive Dateirechte:** State-Verzeichnis, `logs/` und Lock-Datei erhalten
  `0700`, State-/Log-Dateien `0600` — unabhängig davon, ob der Standardpfad oder ein
  expliziter `TESTSLOT_STATE_DIR` genutzt wird. Der Ownership-Token (Bearer) liegt
  im State und ist damit nicht world-readable; `status`/`logs` geben Token nicht aus.
- **DB-Adapter:** `db-refresh`/`db-backup` existieren, sind aber **bewusst ohne
  Credentials nicht verfügbar** und werfen hart einen Fehler (keine Erfolgssimulation).

## Tests

```bash
python3 -m unittest discover -s tests -v   # 35 Tests, u. a. echte 5-Prozess-Konkurrenz
```

Abgedeckte Regressionen (QA Runde 1 + 2): echter paralleler Vergabetest mit 5 CLI-Prozessen
(4 belegt, 5. abgewiesen), Lease-Wechsel mit laufendem Prozess (kein Doppelstart,
`--steal`-Übernahme), `release --keep-process`-Ablehnung, Stale-Timeout-Race
(Startgeneration), dokumentiertes `-- <Kommando>`-CLI, negative bounded-restart-Tests,
aktiver Lease verhindert Idle-Diagnose, Auto-Vergabe überspringt verwaiste Slots,
belegter expliziter Port wird vor Spawn abgelehnt (fremder Listener ≠ eigener Start),
stop während der Erfolgs-Finalisierung wird als abgebrochener Start gemeldet.
Kindprozesse werden deterministisch reaped (keine ResourceWarnings).

Härtungs-Regressionen (Rework t_0744b32c): korrupter State fail-closed mit echtem
Loopback-Prozess (kein Doppelstart, Datei erhalten, dokumentierte Recovery),
isolierter gemockter PID-Identitätsausfall (kein State-Eintrag, kein fremder Kill,
eigenes Kind reapet), kein Kill/keine Übernahme bei unbekannter Startzeit,
Idle-Diagnose seit letztem Heartbeat, POSIX-Modi 0700/0600 bei Standard- und
explizitem Pfad, Token nicht in `status`-Ausgabe.

Integrationstests starten einen realen Dummy-HTTP-Server auf loopback und fragen ihn
per HTTP ab. Kein npm, kein Supabase, kein Docker.

## Grenzen (bewusst)

- Kein VPS-Deployment, keine Cloud-Aktionen, kein Supabase-Start — nur loopback-Prozesse.
- `db-refresh`/`db-backup` nicht verfügbar (Zugänge zur externen Dev-Supabase ungeklärt).
- Keine Secrets: der Manager sammelt/protokolliert keine Credentials.
- State liegt unter `~/.testslot-manager/` (überschreibbar via `TESTSLOT_STATE_DIR`,
  immer `0700`/`0600`-restriktiv).

## Rollback

Der Manager ändert nichts außerhalb seines State-Dirs. Rollback: laufende Slots
`stop`/`release`, dann `rm -rf ~/.testslot-manager` (enthält nur State + Logs).
Keine Installations-Spuren, keine systemweiten Änderungen.
