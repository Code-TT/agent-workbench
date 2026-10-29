#!/usr/bin/env python3
"""
Bestands-Scan für Event-Portal und Crawler: welche Arbeitskopie hat was, was fehlt wo.

Zweck: das ständige Hin und Her ("fehlt das auch noch?") durch einen maschinellen
Bericht ersetzen. Der Planer bekommt damit Fakten statt Erinnerungen.

WICHTIG: Vergleichsbasis ist die jeweilige RECOVERY-BASELINE, nicht `main`.
Die Recovery-Zweige sind auf der Baseline aufgesetzt; ein Vergleich gegen `main`
listet hunderte fremde Dateien mit (gemessen: 400+ statt der echten Änderungen).

Nur lesende git-Befehle. Ausgabe:
  inventory.md    Markdown-Bericht
  inventory.json  maschinenlesbar

Aufruf:
  python3 inventory-worktrees.py
  python3 inventory-worktrees.py --extra-dir /pfad/mit/weitere/worktrees
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
from datetime import datetime, timezone

HOME = pathlib.Path.home()
DEV = HOME / "Documents/Development"
OUT_DIR = pathlib.Path(__file__).resolve().parent

# Pro Repository: Pfad + Baseline (Recovery-Stand), gegen den verglichen wird.
REPOS = {
    "portal": {"path": DEV / "002_EventsPage", "baseline": "39d9500",
               "remote": "Code-TT/EventsPage"},
    "crawler": {"path": DEV / "001_FB_Event_Crawler", "baseline": "57c71a5",
                "remote": "Code-TT/event-crawler"},
}
EXTRA_DIRS = [DEV / "recovery-worktrees"]


def git(path: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout if p.returncode == 0 else p.stderr).strip()


def _common(path: str) -> pathlib.Path | None:
    rc, common = git(path, "rev-parse", "--git-common-dir")
    if rc != 0:
        return None
    c = pathlib.Path(common)
    return (c if c.is_absolute() else (pathlib.Path(path) / c)).resolve()


def repo_of(path: str) -> str | None:
    c = _common(path)
    if c is None:
        return None
    for name, cfg in REPOS.items():
        mc = _common(str(cfg["path"]))
        if mc is not None and str(mc) == str(c):
            return name
    return None


def describe(path: str, base: str) -> dict:
    info: dict = {"pfad": path, "existiert": pathlib.Path(path).is_dir()}
    if not info["existiert"]:
        return info
    rc, head = git(path, "rev-parse", "--short", "HEAD")
    if rc != 0:
        info["fehler"] = head[:200]
        return info
    info["head"] = head
    _, info["branch"] = git(path, "rev-parse", "--abbrev-ref", "HEAD")
    _, info["letzter_commit"] = git(path, "log", "-1", "--pretty=%s")
    _, info["letzter_commit_zeit"] = git(path, "log", "-1", "--pretty=%cI")
    rc, ahead = git(path, "log", "--pretty=%h %s", f"{base}..HEAD")
    info["commits_vor_baseline"] = [l for l in ahead.splitlines() if l.strip()] if rc == 0 else []
    rc, unpushed = git(path, "log", "--oneline", "HEAD", "--not", "--remotes")
    info["unpushed"] = len([l for l in unpushed.splitlines() if l.strip()]) if rc == 0 else None
    rc, stat = git(path, "diff", "--stat", f"{base}...HEAD")
    info["diff_stat"] = stat.splitlines()[-1] if rc == 0 and stat.strip() else "-"
    rc, files = git(path, "diff", "--name-only", f"{base}...HEAD")
    info["dateien"] = [l for l in files.splitlines() if l.strip()] if rc == 0 else []
    rc, dirty = git(path, "status", "--porcelain")
    info["uncommittet"] = [l for l in dirty.splitlines() if l.strip()] if rc == 0 else []
    return info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra-dir", action="append", default=None)
    args = ap.parse_args()
    dirs = [pathlib.Path(d) for d in (args.extra_dir or EXTRA_DIRS)]

    paths: list[str] = []
    for cfg in REPOS.values():
        rc, wt = git(str(cfg["path"]), "worktree", "list", "--porcelain")
        if rc == 0:
            paths += [l[len("worktree "):] for l in wt.splitlines() if l.startswith("worktree ")]
    for base in dirs:
        if base.is_dir():
            paths += [str(d) for d in sorted(base.iterdir()) if d.is_dir() and (d / ".git").exists()]

    seen, entries = set(), []
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        name = repo_of(p)
        base = REPOS[name]["baseline"] if name else "main"
        e = describe(p, base)
        e.update(repo=name or "?", baseline=base,
                 remote=REPOS[name]["remote"] if name else None)
        entries.append(e)

    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    mit = [e for e in entries if e.get("commits_vor_baseline") or e.get("uncommittet")]
    leer = [e for e in entries if e not in mit]

    lines = ["# Bestands-Scan Portal + Crawler", "",
             f"- Zeitpunkt: {stamp}",
             "- Vergleichsbasis: " + ", ".join(f"{k} = `{v['baseline']}`" for k, v in REPOS.items()),
             f"- Arbeitskopien: {len(entries)} (mit eigener Arbeit: {len(mit)})", ""]
    for e in sorted(mit, key=lambda x: -len(x.get("commits_vor_baseline", []))):
        lines += [f"## [{e['repo']}] {e['pfad']}",
                  f"- Branch: `{e.get('branch')}` · HEAD `{e.get('head')}` · Basis `{e['baseline']}`",
                  f"- letzter Commit: {e.get('letzter_commit_zeit')} — {e.get('letzter_commit')}",
                  f"- **Commits über der Baseline: {len(e.get('commits_vor_baseline', []))}**"
                  f" · ungepusht: {e.get('unpushed')} · uncommittet: {len(e.get('uncommittet', []))} Dateien",
                  f"- Umfang: {e.get('diff_stat')}"]
        for c in e.get("commits_vor_baseline", [])[:15]:
            lines.append(f"    - {c}")
        for f in e.get("uncommittet", [])[:15]:
            lines.append(f"    - (uncommittet) {f}")
        if len(e.get("uncommittet", [])) > 15:
            lines.append(f"    - … {len(e['uncommittet']) - 15} weitere")
        lines.append("")
    if leer:
        lines += ["## Ohne eigene Arbeit", ""]
        for e in leer:
            lines.append(f"- [{e['repo']}] {e['pfad']} · `{e.get('branch')}` · `{e.get('head')}`")
    (OUT_DIR / "inventory.md").write_text("\n".join(lines) + "\n")
    (OUT_DIR / "inventory.json").write_text(json.dumps(
        {"zeitpunkt": stamp, "repos": {k: {"pfad": str(v["path"]), "baseline": v["baseline"]}
                                       for k, v in REPOS.items()}, "arbeitskopien": entries},
        indent=1, ensure_ascii=False))

    print(f"{'Repo':8s} {'Arbeitskopie':50s} {'Branch':34s} {'+Commits':>8s} {'dirty':>6s} {'ungesp.':>8s}")
    for e in entries:
        print(f"{e['repo']:8s} {pathlib.Path(e['pfad']).name[:50]:50s} {str(e.get('branch'))[:34]:34s} "
              f"{len(e.get('commits_vor_baseline', [])):8d} {len(e.get('uncommittet', [])):6d} "
              f"{str(e.get('unpushed')):>8s}")
    print(f"\nGeschrieben: {OUT_DIR/'inventory.md'} und inventory.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
