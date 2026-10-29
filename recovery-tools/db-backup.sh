#!/usr/bin/env bash
# db-backup.sh – Sicherung der Live-DB (EventsDB) mit Manifest, Prüfsumme und Aufbewahrung.
#
# Voraussetzung: die Verbindungszeichenfolge liegt als SUPABASE_DB_URL_LIVE in einer
# geschützten Datei (Standard: ~/.hermes/.env, Modus 600). Sie wird NIE ausgegeben.
#
# Aufruf:  ./db-backup.sh            # sichert und räumt alte Sicherungen auf
#          ./db-backup.sh --keep 30  # 30 Tage aufbewahren
set -euo pipefail

# Cron/Hermes-Skriptlauf startet mit reduziertem PATH; docker liegt in /usr/local/bin.
# Ohne diese Ergänzung bricht die Sicherung mit "docker: command not found" ab.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
DOCKER_BIN="$(command -v docker || true)"
if [ -z "$DOCKER_BIN" ]; then
  echo "FEHLT: docker nicht im PATH ($PATH)"; exit 2
fi

SECRETS="${SUPABASE_ENV_FILE:-$HOME/.hermes/.env}"
ZIEL="${BACKUP_DIR:-$HOME/backups/002_EventsPage}"
KEEP=14
PG_IMAGE="postgres:17"

while [ $# -gt 0 ]; do
  case "$1" in
    --keep) KEEP="$2"; shift 2 ;;
    *) echo "unbekannte Option: $1"; exit 2 ;;
  esac
done

if [ ! -f "$SECRETS" ]; then echo "FEHLT: Secrets-Datei $SECRETS"; exit 2; fi
SUPABASE_DB_URL_LIVE="$(grep -E '^SUPABASE_DB_URL_LIVE=' "$SECRETS" | head -1 | cut -d= -f2- | tr -d '"' || true)"
if [ -z "${SUPABASE_DB_URL_LIVE:-}" ]; then
  echo "FEHLT: SUPABASE_DB_URL_LIVE in $SECRETS"
  echo "Einmalig eintragen (ohne Echo, nicht in den Chat):"
  echo "  printf 'SUPABASE_DB_URL_LIVE=%s\\n' 'postgresql://postgres.<ref>:<passwort>@<host>:5432/postgres' >> $SECRETS"
  echo "  chmod 600 $SECRETS"
  exit 3
fi
export SUPABASE_DB_URL_LIVE   # wird per -e <NAME> an den Container gereicht, nicht als Argument
export PGSSLMODE="${PGSSLMODE:-require}"   # Supabase verlangt SSL ((ESSLREQUIRED))

mkdir -p "$ZIEL"
STAMP="$(date +%Y%m%d_%H%M%S)"
DUMP="$ZIEL/eventsdb_${STAMP}.dump"
MANIFEST="$ZIEL/eventsdb_${STAMP}.manifest.txt"

echo "== Sicherung der Live-DB nach $DUMP =="
# pg_dump läuft im Container (auf dem Host ist kein pg_dump installiert).
OUT_NAME="$(basename "$DUMP")"; export OUT_NAME
if ! docker run --rm -e PGCONNECT_TIMEOUT=60 -e SUPABASE_DB_URL_LIVE -e PGSSLMODE -e OUT_NAME -v "$ZIEL":/out "$PG_IMAGE" \
     sh -c 'pg_dump --no-owner --no-privileges --format=custom -d "$SUPABASE_DB_URL_LIVE" -f "/out/$OUT_NAME"'; then
  echo "FEHLER: pg_dump ist fehlgeschlagen – Ausgabe oben. Keine Sicherung erzeugt."; exit 4
fi
if [ ! -s "$DUMP" ]; then echo "FEHLER: Sicherungsdatei fehlt oder ist leer: $DUMP"; exit 5; fi

GROESSE="$(stat -f %z "$DUMP")"
SUMME="$(shasum -a 256 "$DUMP" | awk '{print $1}')"
INHALT="$(docker run --rm -v "$ZIEL":/out "$PG_IMAGE" sh -c "pg_restore --list /out/$(basename "$DUMP") | wc -l" | tr -d ' ')"

{
  echo "# Sicherung EventsDB (Live)"
  echo "Zeitpunkt:   $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Datei:       $(basename "$DUMP")"
  echo "Größe:       ${GROESSE} Bytes"
  echo "SHA256:      ${SUMME}"
  echo "pg_restore-Objekte: ${INHALT}"
  echo "Wiederherstellen (Probe): ./db-restore-test.sh"
} > "$MANIFEST"

echo "  Größe:   ${GROESSE} Bytes"
echo "  SHA256:  ${SUMME}"
echo "  Objekte: ${INHALT}"
echo "  Manifest: $MANIFEST"

echo "== Aufbewahrung: ältere als ${KEEP} Tage entfernen (die letzten 3 bleiben immer) =="
ls -1t "$ZIEL"/eventsdb_*.dump 2>/dev/null | tail -n +4 | while read -r f; do
  if [ -n "$(find "$f" -mtime "+${KEEP}" 2>/dev/null)" ]; then
    rm -f "$f" "${f%.dump}.manifest.txt"; echo "  entfernt: $(basename "$f")"
  fi
done
echo "Fertig. Sicherung liegt unter $ZIEL"
