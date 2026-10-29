#!/usr/bin/env python3
"""
catalog.py — Zielzustand-Katalog: welche Seiten, Routen und Doku-Bausteine gibt es,
und in welchen Quellen liegt welche Fassung?

Read-only. Schreibt nur nach work/.

    python3 catalog.py

Ausgabe:
    work/zielzustand-katalog.md    lesbares Inventar (Routen + Kandidatenstatus)
    work/zielzustand-katalog.json  maschinenlesbar
"""
import collections
import datetime as dt
import hashlib
import json
import pathlib
import sqlite3
import subprocess
import sys

HOME = pathlib.Path.home()
WORK = pathlib.Path(__file__).resolve().parent / "work"
DEV = HOME / "Documents/Development"
REC = HOME / "Desktop/RECOVERY_INTERNAL"
PORTAL = DEV / "002_EventsPage"


def sha(p: pathlib.Path):
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None


def sources():
    """(Name, Wurzel) für die Suche nach Kandidaten."""
    out = [("aktiv", PORTAL), ("archiv", REC / "002_EventsPage"),
           ("hermes-snapshot", REC / "EMERGENCY_RECOVERY/hermes_sessions_recovery"),
           ("vscode-snapshot", REC / "EMERGENCY_RECOVERY/vscode_recovery_20261007_001615")]
    for base in (DEV / "recovery-worktrees", PORTAL / ".worktrees"):
        if base.is_dir():
            for d in sorted(base.iterdir()):
                if d.is_dir():
                    out.append((f"wt:{d.name}", d))
    return out


def routes_of(root: pathlib.Path):
    """Alle Routendateien unter app/."""
    app = root / "app"
    if not app.is_dir():
        return set()
    found = set()
    for p in app.rglob("*"):
        if not p.is_file():
            continue
        name = p.name
        if name in ("page.tsx", "route.ts", "layout.tsx", "opengraph-image.tsx"):
            found.add(str(p.relative_to(root)))
    return found


def main():
    srcs = sources()
    print("Quellen:")
    for n, r in srcs:
        print(f"  {n:<20} {'OK' if r.is_dir() else 'FEHLT'}  {r}")

    # ---- Routen: Vereinigung ueber alle Quellen ----
    per_source = {}
    for n, r in srcs:
        per_source[n] = routes_of(r)
    all_routes = sorted(set().union(*per_source.values()))

    rows = []
    for rel in all_routes:
        cands = []
        for n, r in srcs:
            f = r / rel
            if f.is_file():
                st = f.stat()
                cands.append({"source": n, "bytes": st.st_size, "sha256": sha(f)})
        shas = {c["sha256"] for c in cands}
        if len(cands) <= 1:
            status = "nur-eine-quelle"
        elif len(shas) == 1:
            status = "identisch"
        else:
            status = "varianten"
        kind = pathlib.Path(rel).name.replace(".tsx", "").replace(".ts", "")
        area = rel.split("/")[1] if len(rel.split("/")) > 1 else "?"
        rows.append({"route": rel, "kind": kind, "area": area, "status": status,
                     "n_quellen": len(cands),
                     "groessen": "|".join(f"{c['source']}={c['bytes']}" for c in cands)})

    # ---- Doku-Bausteine ----
    docs = {}
    for label, rel_dir, glob in (
        ("Features (aktiv)", "features", "*.md"),
        ("Features (archiv)", None, None),
        ("Doku (docs)", "docs", "**/*.md"),
        ("Issues (issues)", "issues", "*.md"),
        ("AGENTS/WORKFLOW/README", ".", "*.md"),
    ):
        if rel_dir is None:
            d = REC / "002_EventsPage" / "features"
            if d.is_dir():
                docs[label] = sorted(p.name for p in d.glob("*.md"))
            continue
        d = PORTAL / rel_dir
        if d.is_dir():
            docs[label] = sorted(str(p.relative_to(PORTAL)) for p in d.glob(glob))

    # ---- Kanban-Auftraege (read-only) ----
    cards = []
    db = HOME / ".hermes/kanban.db"
    if db.is_file():
        try:
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            con.row_factory = sqlite3.Row
            for r in con.execute(
                "select id, title, assignee, status, created_at from tasks "
                "where created_at >= ? order by created_at",
                (dt.datetime(2026, 9, 20).timestamp(),),
            ):
                cards.append({"id": r["id"], "title": r["title"], "assignee": r["assignee"],
                              "status": r["status"],
                              "created": dt.datetime.fromtimestamp(r["created_at"]).strftime("%Y-%m-%d")})
            con.close()
        except Exception as e:
            print("Kanban nicht lesbar:", e)

    counts = collections.Counter(r["status"] for r in rows)
    areas = collections.Counter(r["area"] for r in rows)

    summary = {
        "quellen": [n for n, r in srcs if r.is_dir()],
        "routen_gesamt": len(rows),
        "routen_status": dict(counts),
        "routen_je_bereich": dict(areas.most_common()),
        "doku": {k: len(v) for k, v in docs.items()},
        "kanban_karten": len(cards),
        "varianten": [r["route"] for r in rows if r["status"] == "varianten"],
    }
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "zielzustand-katalog.json").write_text(
        json.dumps({"summary": summary, "routen": rows, "doku": docs, "kanban": cards},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Zielzustand-Katalog (mechanisch erzeugt)", "",
          f"Routen insgesamt: **{len(rows)}** · Quellen: {len(srcs)}", "",
          "## Routen nach Status", "", "| Status | Anzahl |", "|---|---|"]
    for k, v in counts.most_common():
        md.append(f"| {k} | {v} |")
    md += ["", "## Routen nach Bereich", "", "| Bereich | Routen |", "|---|---|"]
    for k, v in areas.most_common():
        md.append(f"| {k} | {v} |")
    md += ["", "## Routen mit Varianten (Entscheidung nötig)", "",
           "| Route | Bereich | Quellen/Größen |", "|---|---|---|"]
    for r in rows:
        if r["status"] == "varianten":
            md.append(f"| `{r['route']}` | {r['area']} | {r['groessen']} |")
    md += ["", "## Doku-Bausteine", ""]
    for k, v in docs.items():
        md.append(f"**{k}** ({len(v)})")
        for f in v[:40]:
            md.append(f"- `{f}`")
        if len(v) > 40:
            md.append(f"- … {len(v)-40} weitere")
        md.append("")
    md += ["## Kanban-Arbeitsaufträge (ab 20.09.)", "",
           "| Datum | Karte | Assignee | Status |", "|---|---|---|---|"]
    for c in cards[:80]:
        md.append(f"| {c['created']} | {c['title'][:70]} | {c['assignee']} | {c['status']} |")
    (WORK / "zielzustand-katalog.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\nRouten: {len(rows)}  Status: {dict(counts)}")
    print(f"Varianten (Entscheidung nötig): {len(summary['varianten'])}")
    print(f"Doku: " + ", ".join(f"{k}={len(v)}" for k, v in docs.items()))
    print(f"Kanban-Karten ab 20.09.: {len(cards)}")
    print(f"\nMD:  {WORK/'zielzustand-katalog.md'}")
    print(f"JSON:{WORK/'zielzustand-katalog.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
