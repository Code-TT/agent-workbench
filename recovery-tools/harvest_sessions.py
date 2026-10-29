#!/usr/bin/env python3
"""
harvest_sessions.py — mechanische Ernte der Datei-Schreiboperationen aus Hermes-Sessions.

Liest state.db (read-only Kopie) aller Profile und schreibt JEDE write_file/patch-Operation
als eine Zeile nach operations.jsonl. Kein LLM, keine Interpretation.

Aufruf:
    python3 harvest_sessions.py                 # alle Profile
    python3 harvest_sessions.py frontend-dev    # nur ein Profil

Output (in _recovery-tools/work/):
    operations.jsonl      eine Zeile je Schreiboperation
    harvest_summary.json  Abdeckung: Sessions, Nachrichten, Zeitraum, Zählungen

Wichtig: liest ausschliesslich Kopien. Die Original-state.db wird nie geöffnet.
"""
import json
import pathlib
import shutil
import sqlite3
import sys

HOME = pathlib.Path.home()
PROFILES = HOME / ".hermes/profiles"
WORK = pathlib.Path(__file__).resolve().parent / "work"
WORK.mkdir(parents=True, exist_ok=True)

# Wurzel -> (Projektkennung, ist_worktree_wurzel). Laengste Uebereinstimmung gewinnt.
ROOTS = [
    ("/Volumes/External Disk/Users/thomas/Documents/Development/002_EventsPage", "portal", False),
    ("/Volumes/External Disk/Users/thomas/Documents/Development/001_FB_Event_Crawler", "crawler", False),
    # Parallel-Worktrees des Portals liegen NICHT unter dem Repo -> eigener Eintrag
    ("/Volumes/External Disk/Users/thomas/Documents/Development/recovery-worktrees", "portal", True),
]
# Kanban-Worker schreiben Dateien ZUERST in ihren Scratch-Workspace und kopieren sie
# danach ins Repo. Ohne diese Regel bleibt der volle Pfad stehen, der erzeugende
# write_file ist dann unter dem Repo-Pfad unsichtbar (echter Fehler, 2026-10-15:
# components/UserProfileModal.tsx war dadurch nicht replaybar).
KANBAN_WS = "/.hermes/kanban/workspaces/"
WRITE_TOOLS = {"write_file", "patch"}


def normalize(raw_path: str):
    """Pfad -> (scope, rel_path, worktree). worktree aus .worktrees/<id>/ bzw. recovery-worktrees/<name>/."""
    p = raw_path.replace("\\", "/")
    if KANBAN_WS in p:
        tail = p.split(KANBAN_WS, 1)[1]
        parts = tail.split("/", 1)
        return "workspace", (parts[1] if len(parts) > 1 else ""), None
    scope, rel, worktree = "other", p, None
    for root, sc, is_wt_root in sorted(ROOTS, key=lambda r: -len(r[0])):
        if p.startswith(root + "/"):
            scope, rel = sc, p[len(root) + 1:]
            if is_wt_root:
                parts = rel.split("/")
                if len(parts) > 1:
                    worktree, rel = parts[0], "/".join(parts[1:])
            break
    if worktree is None and rel.startswith(".worktrees/"):
        parts = rel.split("/")
        if len(parts) > 2:
            worktree, rel = parts[1], "/".join(parts[2:])
    return scope, rel, worktree


def copy_db(src: pathlib.Path, dst_dir: pathlib.Path) -> pathlib.Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "state.db"
    for suf in ("", "-wal", "-shm"):
        s = pathlib.Path(str(src) + suf)
        t = pathlib.Path(str(dst) + suf)
        if s.exists():
            shutil.copy2(s, t)
        elif t.exists():
            t.unlink()
    return dst


def classify_result(content) -> str:
    if content is None:
        return "unknown"
    s = content if isinstance(content, str) else str(content)
    head = s.lstrip()[:200]
    if head.startswith('{"error"') or '"error":' in head[:80]:
        return "error"
    if '"success": true' in head or '"success":true' in head:
        return "ok"
    if '"bytes_written"' in head or '"verified"' in head:
        return "ok"
    if '"diff"' in head:
        return "ok"
    if head.startswith("[write_file] wrote to") or head.startswith("[patch]"):
        return "ok"
    if head.startswith("Error") or "Traceback" in head:
        return "error"
    return "unknown"


def harvest_profile(db_path: pathlib.Path, profile: str, out_fh, stats: dict):
    """Liest eine state.db-Kopie und schreibt Operationen nach out_fh."""
    local = copy_db(db_path, WORK / f"copy-{profile}")
    con = sqlite3.connect(f"file:{local}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    # Ergebnisse (role=tool) je call_id einsammeln -> Erfolg/Nicht-Erfolg.
    # Pro call_id existieren oft ZWEI Zeilen (JSON-Ergebnis + Kurzform
    # "[write_file] wrote to ..."). Immer die informationsreichste behalten.
    results = {}
    for r in con.execute(
        "select tool_call_id, content from messages "
        "where role='tool' and tool_call_id is not null"
    ):
        cid = r["tool_call_id"]
        c = r["content"] or ""
        prev = results.get(cid)
        if prev is None or len(c) > len(prev):
            results[cid] = c

    sessions = {r["id"]: dict(r) for r in con.execute("select * from sessions")}

    q = (
        "select id, session_id, timestamp, tool_calls, reasoning_content "
        "from messages where tool_calls is not null and tool_calls <> '' "
        "order by timestamp"
    )
    n_ops = 0
    for row in con.execute(q):
        try:
            calls = json.loads(row["tool_calls"])
        except Exception:
            continue
        if not isinstance(calls, list):
            continue
        for call in calls:
            fn = (call or {}).get("function") or {}
            name = fn.get("name")
            if name not in WRITE_TOOLS:
                continue
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                args = {}
            raw = args.get("path") or args.get("file_path") or ""
            if not raw:
                continue
            scope, rel, worktree = normalize(raw)
            call_id = call.get("call_id") or call.get("id")
            s = sessions.get(row["session_id"], {})
            rec = {
                "profile": profile,
                "tool": name,
                "op": "write" if name == "write_file" else "patch",
                "raw_path": raw,
                "scope": scope,
                "rel_path": rel,
                "worktree": worktree,
                "ts": row["timestamp"],
                "session_id": row["session_id"],
                "session_cwd": s.get("cwd"),
                "session_git_branch": s.get("git_branch"),
                "call_id": call_id,
                "result": classify_result(results.get(call_id)),
                "content": args.get("content"),
                "old_string": args.get("old_string"),
                "new_string": args.get("new_string"),
                "replace_all": args.get("replace_all"),
            }
            out_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_ops += 1

    st = {
        "sessions": len(sessions),
        "messages": con.execute("select count(*) from messages").fetchone()[0],
        "ts_min": con.execute("select min(timestamp) from messages").fetchone()[0],
        "ts_max": con.execute("select max(timestamp) from messages").fetchone()[0],
        "model": sorted(
            {r["model"] for r in con.execute("select distinct model from sessions") if r["model"]}
        ),
        "ops": n_ops,
    }
    con.close()
    stats[profile] = st
    return n_ops


def main():
    want = sys.argv[1:]
    dbs = []
    base = HOME / ".hermes/state.db"
    if base.exists():
        dbs.append(("default", base))
    if PROFILES.is_dir():
        for p in sorted(PROFILES.iterdir()):
            f = p / "state.db"
            if f.is_file():
                dbs.append((p.name, f))
    if want:
        dbs = [d for d in dbs if d[0] in want]
    if not dbs:
        print("keine state.db gefunden")
        return 1

    out = WORK / "operations.jsonl"
    stats = {}
    total = 0
    with out.open("w", encoding="utf-8") as fh:
        for profile, db in dbs:
            try:
                total += harvest_profile(db, profile, fh, stats)
            except Exception as e:  # kein stiller Abbruch
                stats[profile] = {"error": f"{type(e).__name__}: {e}"}
                print(f"FEHLER {profile}: {e}", file=sys.stderr)

    (WORK / "harvest_summary.json").write_text(
        json.dumps(
            {"profiles": stats, "operations_total": total, "out": str(out)},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Operationen gesamt: {total}  ->  {out}")
    for p, s in stats.items():
        if "error" in s:
            print(f"  {p:<22} FEHLER: {s['error']}")
        else:
            print(
                f"  {p:<22} sessions={s['sessions']:<4} msgs={s['messages']:<6} ops={s['ops']}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
