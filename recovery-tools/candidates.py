#!/usr/bin/env python3
"""
candidates.py — Kandidatenliste fuer eine Datei/ein Glob, aus ALLEN Quellen.

Read-only. Schreibt nichts in Repos. Mischen tut es absichtlich NICHT:
jeder Kandidat behaelt Quelle, Branch/Worktree, Zeit und sha256.

Aufruf:
    python3 candidates.py components/EventDetailEditorial.tsx
    python3 candidates.py 'app/[lang]/events/**'          # Glob relativ zu jedem Baum
    python3 candidates.py <pfad> --baseline recovery/baseline-2026-10-13

Output (in _recovery-tools/work/):
    candidates_<slug>.json     vollstaendige Liste
    candidates_<slug>.txt      lesbare Tabelle

Quellen: Archiv-Repo, aktives Repo, Hermes-Snapshot, VS-Code-Snapshot, alle
Worktree-Wurzeln, git-Objekte aller Branches, Session-Operationen (operations.jsonl).
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import pathlib
import subprocess
import sys

HOME = pathlib.Path.home()
DEV = HOME / "Documents/Development"
WORK = pathlib.Path(__file__).resolve().parent / "work"
REC = HOME / "Desktop/RECOVERY_INTERNAL"
DEFAULT_BASELINE = "recovery/baseline-2026-10-13"


def sh(args, cwd=None):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=90)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def iso(ts):
    if not ts:
        return None
    try:
        return dt.datetime.fromtimestamp(float(ts)).isoformat(timespec="seconds")
    except Exception:
        return str(ts)


def sha256(p: pathlib.Path):
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def fs_source(name, root: pathlib.Path, pattern: str):
    out = []
    if not root.is_dir():
        return out
    # Ohne echte Wildcards direkt pruefen - sonst deutet glob '[lang]' als Zeichenklasse.
    if "*" not in pattern and "?" not in pattern:
        p = root / pattern
        hits = [p] if p.is_file() else []
    else:
        hits = [pathlib.Path(h) for h in glob.glob(str(root / pattern), recursive=True)]
    for p in hits:
        if p.is_file():
            out.append(
                {
                    "source": name,
                    "kind": "file",
                    "path": str(p),
                    "size": p.stat().st_size,
                    "mtime": dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(
                        timespec="seconds"
                    ),
                    "sha256": sha256(p),
                }
            )
    return out


def git_source(name, repo: pathlib.Path, pattern: str, baseline: str):
    """Blobs des Pfads ueber ALLE Branches + Abstand zur Fork-Basis."""
    out = []
    if not (repo / ".git").exists():
        return out
    # exakte Datei (Glob im git-Pfad nur bei einfachem Muster sinnvoll)
    if any(c in pattern for c in "*?["):
        return out
    branches = sh(["git", "-C", str(repo), "for-each-ref",
                   "--format=%(refname:short)", "refs/heads"]).splitlines()
    for b in branches:
        blob = sh(["git", "-C", str(repo), "rev-parse", "--verify", f"{b}:{pattern}"])
        if not blob:
            continue
        last = sh(["git", "-C", str(repo), "log", "-1", "--format=%aI", b, "--", pattern])
        subject = sh(["git", "-C", str(repo), "log", "-1", "--format=%s", b, "--", pattern])
        mb = sh(["git", "-C", str(repo), "merge-base", b, baseline])
        over = (
            len(sh(["git", "-C", str(repo), "rev-list", f"{mb}..{b}"]).splitlines()) if mb else None
        )
        out.append(
            {
                "source": name,
                "kind": "git-blob",
                "branch": b,
                "blob": blob[:40],
                "last_commit_date": last,
                "last_commit_subject": subject,
                "fork_base": mb[:12] if mb else None,
                "commits_over_fork_base": over,
                "path": f"{repo}:{b}:{pattern}",
            }
        )
    return out


def session_source(rel_path: str):
    ops = WORK / "operations.jsonl"
    out = []
    if not ops.is_file():
        return out
    with ops.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("rel_path") != rel_path:
                continue
            out.append(
                {
                    "source": f"session/{r.get('profile')}",
                    "kind": "session-op",
                    "path": r.get("raw_path"),
                    "op": r.get("op"),
                    "tool": r.get("tool"),
                    "result": r.get("result"),
                    "ts": iso(r.get("ts")),
                    "branch": r.get("session_git_branch"),
                    "worktree": r.get("worktree"),
                    "content_len": len(r.get("content") or "") or None,
                    "patch": (r.get("old_string") is not None),
                }
            )
    return out


def discover_roots():
    roots = [
        ("archiv-repo", REC / "002_EventsPage"),
        ("aktiv-repo", DEV / "002_EventsPage"),
        ("hermes-snapshot", REC / "EMERGENCY_RECOVERY/hermes_sessions_recovery"),
        ("vscode-snapshot", REC / "EMERGENCY_RECOVERY/vscode_recovery_20261007_001615"),
        ("recovery-worktrees", DEV / "recovery-worktrees"),
    ]
    for base in (DEV / "002_EventsPage/.worktrees", REC / "002_EventsPage/.worktrees"):
        if base.is_dir():
            for d in sorted(base.iterdir()):
                if d.is_dir():
                    roots.append((f"worktree/{d.name}", d))
    return [(n, p) for n, p in roots if p.exists()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    args = ap.parse_args()
    pattern = args.pattern

    rows = []
    for name, root in discover_roots():
        rows += fs_source(name, root, pattern)
    for name, root in (("archiv-repo", REC / "002_EventsPage"), ("aktiv-repo", DEV / "002_EventsPage")):
        rows += git_source(name, root, pattern, args.baseline)
    if not any(c in pattern for c in "*?["):
        rows += session_source(pattern)

    rows.sort(key=lambda r: (r.get("last_commit_date") or r.get("ts") or r.get("mtime") or ""))

    slug = pattern.replace("/", "_").replace("*", "star").replace("[", "").replace("]", "")[:60]
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / f"candidates_{slug}.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [f"# Kandidaten fuer: {pattern}", f"# {len(rows)} Kandidaten", ""]
    for r in rows:
        k = r["kind"]
        if k == "file":
            lines.append(
                f"{r['source']:<20} file    {r['mtime']}  {r['size']:>8}  {r['sha256'][:16]}"
            )
        elif k == "git-blob":
            lines.append(
                f"{r['source']:<20} git     {r['last_commit_date']}  over_base={r['commits_over_fork_base']}  "
                f"{r['blob'][:12]}  [{r['branch']}] {r['last_commit_subject'][:50]}"
            )
        else:
            lines.append(
                f"{r['source']:<20} session {r['ts']}  {r['op']}/{r['tool']}  result={r['result']}  "
                f"base={r['branch']}"
            )
    txt = "\n".join(lines)
    (WORK / f"candidates_{slug}.txt").write_text(txt, encoding="utf-8")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
