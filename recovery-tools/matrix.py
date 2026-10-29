#!/usr/bin/env python3
"""
matrix.py — Auswahlmatrix fuer alle Dateien, die im Fenster NACH dem Snapshot
bearbeitet wurden.

Read-only. Schreibt nur nach work/.

    python3 matrix.py                    # Fenster: > 07.10.2026 00:48, scope portal
    python3 matrix.py --scope portal --after 2026-10-07T00:48:36

Ausgabe:
    work/auswahlmatrix.csv     eine Zeile pro Datei, eine Spalte je Kennzahl
    work/auswahlmatrix.md      dieselbe Tabelle lesbar
    work/auswahlmatrix.json    Maschinenlesbar inkl. Zusammenfassung
"""
import argparse
import collections
import csv
import datetime as dt
import difflib
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / "work"
HOME = pathlib.Path.home()

# candidates.py als Modul laden (gleiches Verzeichnis)
_spec = importlib.util.spec_from_file_location("cand", HERE / "candidates.py")
cand = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cand)

REC = HOME / "Desktop/RECOVERY_INTERNAL"
MAIN = HOME / "Documents/Development/002_EventsPage"
RW = HOME / "Documents/Development/recovery-worktrees"
HERMES_SNAP = REC / "EMERGENCY_RECOVERY/hermes_sessions_recovery"
VSCODE_SNAP = REC / "EMERGENCY_RECOVERY/vscode_recovery_20261007_001615"
ARCHIVE = REC / "002_EventsPage"
CRAWLER = HOME / "Documents/Development/001_FB_Event_Crawler"
CRAWLER_RW = HOME / "Documents/Development/recovery-worktrees"


def line_delta(a: str, b: str):
    """(hinzugefuegt, entfernt) zwischen zwei Texten. Rein mechanisch."""
    add = rem = 0
    for line in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0):
        if line.startswith("+") and not line.startswith("+++"):
            add += 1
        elif line.startswith("-") and not line.startswith("---"):
            rem += 1
    return add, rem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="portal")
    ap.add_argument("--after", default="2026-10-07T00:48:36")
    args = ap.parse_args()
    cut = dt.datetime.fromisoformat(args.after).timestamp()

    ops = [json.loads(l) for l in (WORK / "operations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    win = [o for o in ops if o.get("scope") == args.scope and o["ts"] > cut and o["result"] == "ok"]

    targets = collections.defaultdict(set)
    for o in win:
        targets[o.get("worktree") or "HAUPTBAUM"].add(o["rel_path"])

    rows = []
    for wt in sorted(targets):
        for rel in sorted(targets[wt]):
            if args.scope == "portal":
                root = MAIN if wt == "HAUPTBAUM" else RW / wt
            else:
                root = CRAWLER if wt == "HAUPTBAUM" else CRAWLER_RW / wt
            wt_file = root / rel

            # Kandidaten sammeln: die eigene Arbeitskopie zuerst
            cands = [{"source": f"worktree:{wt}", "kind": "file", "path": str(wt_file)}]
            for nm, r in (("hauptbaum", MAIN), ("archiv-repo", ARCHIVE),
                          ("hermes-snapshot", HERMES_SNAP), ("vscode-snapshot", VSCODE_SNAP)):
                cands += cand.fs_source(nm, r, rel)
            # dot-worktrees derselben Datei
            for base in (MAIN / ".worktrees", ARCHIVE / ".worktrees"):
                if base.is_dir():
                    for d in sorted(base.iterdir()):
                        if (d / rel).is_file():
                            cands.append({"source": f"worktree:{d.name}", "kind": "file", "path": str(d / rel)})

            files = []
            for c in cands:
                p = pathlib.Path(c["path"])
                if not p.is_file():
                    continue
                b = p.read_bytes()
                files.append({
                    "source": c["source"],
                    "path": str(p),
                    "bytes": len(b),
                    "sha256": cand.sha256(p),
                    "mtime": dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
                })
            # Duplikate (gleicher Pfad/Source) entfernen
            seen, uniq = set(), []
            for f in files:
                k = (f["source"], f["sha256"])
                if k not in seen:
                    seen.add(k)
                    uniq.append(f)
            files = uniq

            shas = {f["sha256"] for f in files}
            n_other = sum(1 for f in files if not f["source"].startswith("worktree:"))
            if len(files) <= 1:
                status = "nur-eine-quelle"
            elif len(shas) == 1:
                status = "identisch"
            elif n_other == 0:
                status = "nur-worktrees-verschieden"
            else:
                status = "verschieden"

            add = rem = 0
            if status in ("verschieden", "nur-worktrees-verschieden"):
                wt_f = next((f for f in files if f["source"].startswith("worktree:")), None)
                other_f = next((f for f in files if not f["source"].startswith("worktree:")), None)
                if wt_f and other_f:
                    try:
                        a = pathlib.Path(other_f["path"]).read_text(errors="replace")
                        b = pathlib.Path(wt_f["path"]).read_text(errors="replace")
                        add, rem = line_delta(a, b)
                    except Exception:
                        pass

            rows.append({
                "worktree": wt,
                "datei": rel,
                "status": status,
                "kandidaten": len(files),
                "zweite_quelle": n_other,
                "varianten": len(shas),
                "groessen": "|".join(f"{f['source']}={f['bytes']}" for f in files),
                "sha256": "|".join(f["sha256"][:12] for f in files),
                "quellen": "|".join(f["source"] for f in files),
                "zeilen_plus": add,
                "zeilen_minus": rem,
            })

    WORK.mkdir(parents=True, exist_ok=True)
    cols = ["worktree", "datei", "status", "kandidaten", "zweite_quelle", "varianten",
            "groessen", "sha256", "quellen", "zeilen_plus", "zeilen_minus"]
    with (WORK / "auswahlmatrix.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    counts = collections.Counter(r["status"] for r in rows)
    summary = {
        "scope": args.scope,
        "after": args.after,
        "ops_im_fenster": len(win),
        "dateien": len(rows),
        "status": dict(counts),
        "je_worktree": dict(collections.Counter(r["worktree"] for r in rows)),
        "verschieden": [f"{r['worktree']}/{r['datei']}" for r in rows if r["status"].startswith("verschieden") or r["status"] == "nur-worktrees-verschieden"],
        "nur_eine_quelle": [f"{r['worktree']}/{r['datei']}" for r in rows if r["status"] == "nur-eine-quelle"],
    }
    (WORK / "auswahlmatrix.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# Auswahlmatrix ({args.scope}, nach {args.after})", "",
          f"Operationen im Fenster: {len(win)} · Dateien: {len(rows)}", "",
          "| Status | Dateien |", "|---|---|"]
    for k, v in counts.most_common():
        md.append(f"| {k} | {v} |")
    md += ["", "| Worktree | Datei | Status | Kandidaten | Quellen | ± Zeilen |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['worktree']} | `{r['datei']}` | {r['status']} | {r['kandidaten']} | "
                  f"{r['quellen']} | +{r['zeilen_plus']}/-{r['zeilen_minus']} |")
    (WORK / "auswahlmatrix.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"Fenster: {len(win)} Ops -> {len(rows)} Dateien (scope={args.scope}, after={args.after})")
    for k, v in counts.most_common():
        print(f"  {k:<26} {v}")
    print(f"\nCSV:  {WORK/'auswahlmatrix.csv'}")
    print(f"MD:   {WORK/'auswahlmatrix.md'}")
    print(f"JSON: {WORK/'auswahlmatrix.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
