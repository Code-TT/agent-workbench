#!/usr/bin/env bash
# db-restore-test.sh – beweist, dass die letzte Sicherung vollständig wiederherstellbar ist.
#
# Ziel ist der lokale Supabase-Stack (supabase_db_002_EventsPage): nur dort stimmen Rollen,
# Schemas und Extensions mit dem Herkunftssystem überein. Ein nacktes postgres:17 scheitert
# an PostGIS bzw. am `extensions`-Schema und lässt events/locations weg.
#
# Aufruf:  ./db-restore-test.sh [pfad/zur/sicherung.dump]
set -euo pipefail

# Cron/Hermes-Skriptlauf startet mit reduziertem PATH; docker liegt in /usr/local/bin.
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

ZIEL="${BACKUP_DIR:-$HOME/backups/002_EventsPage}"
CONTAINER="${SUPABASE_LOCAL_CONTAINER:-supabase_db_002_EventsPage}"
DB="${PROBE_DB:-restore_probe_auto}"
SECRETS="${SUPABASE_ENV_FILE:-$HOME/.hermes/.env}"
DUMP="${1:-$(ls -1t "$ZIEL"/eventsdb_*.dump 2>/dev/null | head -1 || true)}"
TABELLEN="${KERNTABELLEN:-events locations crawler_crawl_proposals album_photos cities profiles event_translations}"
PG_IMAGE="postgres:17"

if [ -z "${DUMP:-}" ] || [ ! -f "$DUMP" ]; then echo "Keine Sicherung gefunden - zuerst ./db-backup.sh"; exit 2; fi
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Lokaler Supabase-Stack laeuft nicht ($CONTAINER)." >&2; exit 2
fi

SUPABASE_DB_URL_LIVE="$(grep -E '^SUPABASE_DB_URL_LIVE=' "$SECRETS" | head -1 | cut -d= -f2- | tr -d '"' || true)"
export SUPABASE_DB_URL_LIVE PGSSLMODE="${PGSSLMODE:-require}"

echo "== Restore-Probe =="
echo "  Sicherung: $(basename "$DUMP")  ($(stat -f %z "$DUMP") Bytes)"
echo "  SHA256:    $(shasum -a 256 "$DUMP" | awk '{print $1}')"
echo "  Ziel:      $CONTAINER / DB $DB"

docker exec "$CONTAINER" sh -c "dropdb --if-exists -U postgres $DB >/dev/null 2>&1; createdb -U postgres $DB"

docker exec "$CONTAINER" psql -U postgres -d "$DB" -q -c \
  "create schema if not exists extensions; create schema if not exists vault;" >/dev/null 2>&1 || true
for ext in postgis pgcrypto; do
  docker exec "$CONTAINER" psql -U postgres -d "$DB" -tAc \
    "create extension if not exists $ext with schema extensions" >/dev/null 2>&1 || true
done
docker exec "$CONTAINER" psql -U postgres -d "$DB" -tAc \
  "create extension if not exists \"uuid-ossp\" with schema extensions" >/dev/null 2>&1 || true

docker cp "$DUMP" "$CONTAINER:/tmp/restore_probe.dump" >/dev/null
FEHLER="$(docker exec "$CONTAINER" pg_restore --no-owner --no-privileges -U postgres -h 127.0.0.1 \
  -d "$DB" /tmp/restore_probe.dump 2>&1 | grep -c "error" || true)"
docker exec "$CONTAINER" rm -f /tmp/restore_probe.dump

echo "  pg_restore-Meldungen mit 'error': ${FEHLER}  (Rollen/Rechte duerfen fehlen - die Zahlen entscheiden)"
echo
printf "  %-26s %8s %8s  %s\n" "Tabelle" "Live" "Restore" "Bewertung"
ABWEICHUNG=0
for t in $TABELLEN; do
  L="$(docker run --rm -e SUPABASE_DB_URL_LIVE -e PGSSLMODE "$PG_IMAGE" sh -c \
       "psql \"\$SUPABASE_DB_URL_LIVE\" -tAc \"select case when to_regclass('public.$t') is null then '-' else (select count(*)::text from public.$t) end\"" 2>/dev/null | tr -d ' ')"
  R="$(docker exec "$CONTAINER" psql -U postgres -d "$DB" -tAc \
       "select case when to_regclass('public.$t') is null then '-' else (select count(*)::text from public.$t) end" 2>/dev/null | tr -d ' ')"
  if [ -n "$L" ] && [ "$L" = "$R" ]; then MARK="identisch"; else MARK="ABWEICHUNG"; ABWEICHUNG=$((ABWEICHUNG+1)); fi
  printf "  %-26s %8s %8s  %s\n" "$t" "${L:--}" "${R:--}" "$MARK"
done
echo
docker exec "$CONTAINER" psql -U postgres -d "$DB" -tAc \
  "select '    Tabellen(public): '||count(*) from information_schema.tables where table_schema='public'" 2>/dev/null
docker exec "$CONTAINER" psql -U postgres -d "$DB" -tAc \
  "select '    RLS-Policies:     '||count(*) from pg_policies" 2>/dev/null
echo
if [ "$ABWEICHUNG" -eq 0 ]; then
  echo "ERGEBNIS: Sicherung ist vollstaendig wiederherstellbar (alle Kerntabellen identisch)."
else
  echo "ERGEBNIS: ${ABWEICHUNG} Abweichung(en) - Sicherung nicht als gueltig behandeln."
  exit 1
fi
