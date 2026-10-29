#!/usr/bin/env bash
# dev-preview.sh — startet einen Dev-Server für einen Worktree und macht ihn prüfbar.
#
# Warum: QA-/Frontend-Worker sind wiederholt daran gescheitert, dass "irgendwo" ein
# Server laufen sollte (toter Port), oder dass der Keycloak-Rückweg auf den falschen
# Port zeigte. Dieses Skript macht daraus einen reproduzierbaren Schritt.
#
# Aufruf:
#   dev-preview.sh <worktree-pfad> [port]
#   dev-preview.sh <worktree-pfad> --stop      (Server dieses Worktrees beenden)
#
# Was es tut:
#   1. freien Port bestimmen (Standard 3115, sonst nächster freier ab 3115)
#   2. NEXTAUTH_URL + NEXT_PUBLIC_APP_URL in der .env.local des Worktrees auf diesen
#      Port setzen (Sicherung AUSSERHALB des Repos — sie enthält Secrets)
#   3. ./node_modules/.bin/next dev starten (nicht `npx next`)
#   4. auf Bereitschaft warten (max. 240 s) und /admin einmal aufrufen
#   5. URL, PID, Logpfad ausgeben
set -uo pipefail

WT="${1:-}"; MODE="${2:-}"
[ -n "$WT" ] || { echo "Aufruf: dev-preview.sh <worktree-pfad> [port|--stop]"; exit 2; }
[ -d "$WT" ] || { echo "Worktree nicht gefunden: $WT"; exit 2; }
WT="$(cd "$WT" && pwd)"
NAME="$(basename "$WT")"
RUNDIR="$HOME/.hermes/cache/scratch/dev-preview"
mkdir -p "$RUNDIR"
PIDFILE="$RUNDIR/$NAME.pid"
LOGFILE="$RUNDIR/$NAME.log"

if [ "$MODE" = "--stop" ]; then
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")" && echo "gestoppt: $NAME (PID $(cat "$PIDFILE"))"
    rm -f "$PIDFILE"
  else
    echo "kein laufender Preview-Server für $NAME"
    pkill -f "next dev --port .*$WT" 2>/dev/null && echo "verwaisten Prozess beendet" || true
  fi
  exit 0
fi

# läuft schon?
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "läuft bereits: $NAME (PID $(cat "$PIDFILE")) — Log: $LOGFILE"
  exit 0
fi

# 1) Port
PORT="${MODE}"
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  PORT=3115
  while lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; do PORT=$((PORT+1)); done
fi
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT ist belegt — bitte anderen Port angeben."; exit 1
fi

# 2) Env anpassen (Sicherung außerhalb des Repos!)
ENVF="$WT/.env.local"
if [ -f "$ENVF" ]; then
  ZIEL="$HOME/backups/002_EventsPage/worktree-env-backups"
  mkdir -p "$ZIEL"; chmod 700 "$ZIEL" 2>/dev/null
  cp "$ENVF" "$ZIEL/$NAME--env.local.vor-preview-$(date +%Y%m%d_%H%M%S)"
  python3 - "$ENVF" "$PORT" <<'PY'
import sys, pathlib
f, port = pathlib.Path(sys.argv[1]), sys.argv[2]
lines = f.read_text().splitlines()
def setz(k, v):
    for i, l in enumerate(lines):
        if l.startswith(k + "="):
            lines[i] = f"{k}={v}"; return
    lines.append(f"{k}={v}")
setz("NEXTAUTH_URL", f"http://localhost:{port}")
setz("NEXT_PUBLIC_APP_URL", f"http://localhost:{port}")
f.write_text("\n".join(lines) + "\n")
PY
  echo "  .env.local: NEXTAUTH_URL/NEXT_PUBLIC_APP_URL -> http://localhost:$PORT"
fi

# 3) Server starten
cd "$WT" || exit 1
[ -x ./node_modules/.bin/next ] || { echo "next nicht installiert — zuerst npm install --legacy-peer-deps"; exit 1; }
nohup ./node_modules/.bin/next dev --port "$PORT" > "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"
echo "  gestartet: $NAME auf Port $PORT (PID $(cat "$PIDFILE"))"

# 4) Auf Bereitschaft warten
echo -n "  warte auf Bereitschaft"
for i in $(seq 1 80); do
  if curl -s -o /dev/null --max-time 3 "http://localhost:$PORT/" 2>/dev/null; then echo " — bereit nach ~$((i*3))s"; break; fi
  echo -n "."; sleep 3
done
if ! curl -s -o /dev/null --max-time 3 "http://localhost:$PORT/" 2>/dev/null; then
  echo; echo "  NICHT bereit. Letzte Logzeilen:"; tail -8 "$LOGFILE" | sed 's/^/    /'; exit 1
fi

# 5) Admin prüfen (erster Aufruf kompiliert)
echo -n "  /admin: "
curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" --max-time 240 "http://localhost:$PORT/admin"

cat <<INFO

  URL    : http://localhost:$PORT
  Admin  : http://localhost:$PORT/admin
  Log    : $LOGFILE
  Stoppen: bash $0 "$WT" --stop
INFO
