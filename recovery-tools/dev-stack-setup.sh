#!/usr/bin/env bash
# dev-stack-setup.sh — stellt die lokale Dev-/QA-Umgebung für das Event-Portal her.
#
# Was es tut:
#   1. lokalen Supabase-Stack starten (idempotent)
#   2. echte Daten aus der jüngsten Live-Sicherung in die lokale Standard-DB laden
#      (nur wenn dort keine Events liegen — sonst bleibt alles unangetastet)
#   3. Standard-Rechte im Schema public setzen (überlebt `drop schema public cascade`)
#   4. .env.local in allen Worktrees auf den LOKALEN Stack umstellen (Originale werden gesichert)
#   5. API-Gegenprobe (HTTP 200)
#
# Warum die Schritte 3 und 4 so aussehen, steht in Obsidian:
#   "Projekte/Event Portal (Community)/Lokale Dev-Umgebung (Supabase-Stack).md"
#
# Aufruf:  bash dev-stack-setup.sh            # alles
#          SKIP_ENV=1 bash dev-stack-setup.sh # nur Stack + Daten, Worktree-Envs unberührt
set -uo pipefail

PROJ="${PROJ:-$HOME/Documents/Development/002_EventsPage}"
BACKUPDIR="${BACKUPDIR:-$HOME/backups/002_EventsPage}"
DB_CONT="supabase_db_002_EventsPage"
WT_DIR="$(dirname "$PROJ")/recovery-worktrees"
TS="$(date +%Y%m%d_%H%M%S)"

step() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()   { printf '   ok  %s\n' "$*"; }
warn() { printf '   !!  %s\n' "$*"; }

[ -d "$PROJ" ] || { warn "Projektverzeichnis fehlt: $PROJ"; exit 1; }
cd "$PROJ" || exit 1

# ---------------------------------------------------------------- 1. Stack
step "1/5  Supabase-Stack starten"
if docker ps --format '{{.Names}}' | grep -qx "$DB_CONT"; then
  ok "Stack läuft bereits"
else
  supabase start >/dev/null 2>&1 || { warn "supabase start fehlgeschlagen"; exit 1; }
  ok "Stack gestartet"
fi

# ---------------------------------------------------------------- 2. Daten
step "2/5  Echte Daten in der lokalen DB prüfen"
ist_events="$(docker exec "$DB_CONT" psql -U postgres -d postgres -tAc \
  "select count(*) from public.events" 2>/dev/null | tr -d ' ' || echo 0)"
soll_events="$(docker run --rm -v "$BACKUPDIR":/b postgres:17 sh -c \
  'ls -t /b/eventsdb_*.dump 2>/dev/null | head -1' 2>/dev/null)"
[ -n "$soll_events" ] || { warn "keine Live-Sicherung in $BACKUPDIR gefunden"; exit 1; }
DUMP="$BACKUPDIR/$(basename "$soll_events")"

if [ "${ist_events:-0}" -gt 0 ]; then
  ok "lokale DB hat bereits $ist_events Events — Daten werden nicht erneut geladen"
else
  warn "lokale DB ist leer (events=$ist_events) — Live-Daten werden geladen"
  docker exec "$DB_CONT" pg_dump -U postgres -d postgres -Fc -f /tmp/pre.dump \
    && docker cp "$DB_CONT":/tmp/pre.dump "$BACKUPDIR/localstack_default_vorher_$TS.dump" >/dev/null \
    && ok "vorheriger Stand gesichert: localstack_default_vorher_$TS.dump"

  docker cp "$DUMP" "$DB_CONT":/tmp/live.dump >/dev/null
  # public leeren. Wichtig: PostGIS liegt auf dem Live-System im Schema `extensions`;
  # lokal liegt es in `public` — liegt es noch dort, scheitern alle Geo-Spalten (geography).
  docker exec "$DB_CONT" psql -U postgres -d postgres -q -c \
    "drop schema public cascade; create schema public; drop extension if exists postgis cascade;" >/dev/null 2>&1
  docker exec "$DB_CONT" pg_restore --no-owner -U postgres -d postgres /tmp/live.dump >/dev/null 2>&1
  ok "Dump eingespielt: $(basename "$DUMP") (Fehler zu Supabase-internen Schemata sind normal)"
fi

# ---------------------------------------------------------------- 3. Rechte
step "3/5  Standard-Rechte im Schema public setzen"
# `drop schema public cascade` löscht die Supabase-Grundrechte mit: danach antwortet die API
# mit 401/42501 "permission denied for schema public", obwohl die Tabellen existieren.
docker exec -i "$DB_CONT" psql -U postgres -d postgres -q <<'SQL' >/dev/null 2>&1
grant usage on schema public to anon, authenticated, service_role;
grant all on all tables in schema public to anon, authenticated, service_role;
grant all on all routines in schema public to anon, authenticated, service_role;
grant all on all sequences in schema public to anon, authenticated, service_role;
alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
alter default privileges in schema public grant all on routines to anon, authenticated, service_role;
alter default privileges in schema public grant all on sequences to anon, authenticated, service_role;
grant usage on schema extensions to anon, authenticated, service_role;
notify pgrst, 'reload schema';
SQL
ok "Rechte gesetzt, Schema-Cache neu geladen"

# ---------------------------------------------------------------- 4. Worktree-Envs
if [ "${SKIP_ENV:-0}" = "1" ]; then
  step "4/5  Worktree-.env.local  — übersprungen (SKIP_ENV=1)"
else
  step "4/5  Worktree-.env.local auf den lokalen Stack umstellen"
  python3 - "$PROJ" "$WT_DIR" "$TS" <<'PY'
import subprocess, pathlib, shutil, sys
P, WT, TS = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
raw = subprocess.run(['supabase','status','-o','env'], cwd=str(P), capture_output=True, text=True).stdout
e = {l.split('=',1)[0]: l.split('=',1)[1].strip().strip('"') for l in raw.splitlines() if '=' in l}
U, PUB, SEC = e['API_URL'], e['PUBLISHABLE_KEY'], e['SECRET_KEY']
DB = 'postgresql://postgres:postgres@127.0.0.1:54322/postgres'
src = (P/'.env.local').read_text()

def anpassen(t):
    out = []
    for l in t.splitlines():
        if   l.startswith('NEXT_PUBLIC_SUPABASE_URL='):              out.append(f'NEXT_PUBLIC_SUPABASE_URL={U}')
        elif l.startswith('NEXT_PUBLIC_SUPABASE_ANON_KEY='):         out.append(f'NEXT_PUBLIC_SUPABASE_ANON_KEY={PUB}')
        elif l.startswith('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY='):  out.append(f'NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY={PUB}')
        elif l.startswith('SUPABASE_SERVICE_ROLE_KEY='):             out.append(f'SUPABASE_SERVICE_ROLE_KEY={SEC}')
        elif l.startswith('SUPABASE_CONNECTION_STRING='):            out.append(f'SUPABASE_CONNECTION_STRING={DB}')
        else: out.append(l)
    if not any(l.startswith('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=') for l in out):
        out.append(f'NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY={PUB}')
    kopf = ('# DEV/QA-Umgebung -> LOKALER Supabase-Stack (127.0.0.1:54321), NICHT Produktion.\n'
            '# Echte Daten (Stand Live-Sicherung). Angelegt/aktualisiert am %s.\n' % TS)
    return kopf + "\n".join(out) + "\n"

if WT.is_dir():
    for d in sorted(WT.iterdir()):
        if not d.is_dir():
            continue
        f = d/'.env.local'
        vorher = {}
        if f.exists():
            # Sicherung NICHT im Repo-Verzeichnis ablegen: sie enthält Secrets, und das
            # Muster `.env*.local` in .gitignore greift für Namen mit Zusatz NICHT —
            # die Datei wäre dann als untracked Datei im Repo (Commit-Gefahr).
            ZIEL = pathlib.Path.home()/'backups'/'002_EventsPage'/'worktree-env-backups'
            ZIEL.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copy2(f, ZIEL/f'{d.name}--env.local.sicherung-{TS}')
            # Port-Einstellungen eines bereits laufenden Preview-Servers erhalten —
            # sonst zeigt der Keycloak-Rückweg wieder auf den Port der Hauptkopie und
            # der Login schlägt fehl (Fehler 'keycloak', callbackUrl Port 3000).
            for l in f.read_text().splitlines():
                if l.startswith(('NEXTAUTH_URL=', 'NEXT_PUBLIC_APP_URL=')):
                    vorher[l.split('=', 1)[0]] = l
        neu = anpassen(src)
        for k, v in vorher.items():
            zeilen = neu.splitlines()
            for i, l in enumerate(zeilen):
                if l.startswith(k + '='):
                    zeilen[i] = v
                    break
            else:
                zeilen.append(v)
            neu = '\n'.join(zeilen).rstrip('\n') + '\n'
        f.write_text(neu)
        print(f'   ok  {d.name}')
else:
    print(f'   !!  Worktree-Verzeichnis fehlt: {WT}')
PY
fi

# ---------------------------------------------------------------- 5. Gegenprobe
step "5/5  Gegenprobe über die API"
eval "$(supabase status -o env 2>/dev/null | grep -E '^(API_URL|PUBLISHABLE_KEY)=')"
code="$(curl -s -o /dev/null -w '%{http_code}' "$API_URL/rest/v1/locations?select=name&limit=1" \
        -H "apikey: $PUBLISHABLE_KEY" --max-time 10)"
anz="$(docker exec "$DB_CONT" psql -U postgres -d postgres -tAc \
        "select count(*) from public.events" 2>/dev/null | tr -d ' ')"
echo "   API $API_URL -> HTTP $code   |   events lokal: $anz"
[ "$code" = "200" ] && ok "Dev-Umgebung einsatzbereit" || warn "API antwortet $code — Rechte/Schlüssel prüfen"

cat <<'TIPP'

Nächste Schritte für Dev/QA:
  • Dev-Server neu starten (Next.js liest .env.local nur beim Serverstart)
  • Studio:      http://127.0.0.1:54323
  • DB direkt:   psql postgresql://postgres:postgres@127.0.0.1:54322/postgres
  • Stack aus:   cd "$PROJ" && supabase stop      (Daten bleiben im Volume)
TIPP
