#!/usr/bin/env python3
"""
replay.py — wendet die geernteten Schreiboperationen EINER Datei in Zeitfolge an
und erzeugt den Kandidaten fuer den letzten Stand.

Read-only gegenueber allen Repos: schreibt nur nach _recovery-tools/work/replay/.

Aufruf:
    python3 replay.py extension/popup.js
    python3 replay.py extension/popup.js --base-file <pfad>   # Basis erzwingen
    python3 replay.py extension/popup.js --compare <pfad>...  # Ergebnis gegen Kandidaten

Regeln (aus den echten Fallstricken):
  * gemeinsame Zeitleiste NUR fuer Ops auf derselben Arbeitskopie (gleicher Worktree);
    unterschiedliche Worktrees werden als getrennte Ketten behandelt.
  * nur result == "ok" zaehlt; Ops mit Warnung im Ergebnis werden markiert.
  * die Basis ist der Stand VOR der ersten Operation, nicht der erste Write.
  * patch: exakt, sonst zeilenweise normalisiert; mehrdeutig = Kette ab hier "partial".
  * was nicht passt, wird BERICHET, nicht geraten.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

HOME = pathlib.Path.home()
WORK = pathlib.Path(__file__).resolve().parent / "work"


def iso(ts):
    try:
        return dt.datetime.fromtimestamp(float(ts)).isoformat(timespec="seconds")
    except Exception:
        return str(ts)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def norm_ws(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.replace("\r\n", "\n").split("\n"))


def norm_indent(s: str) -> str:
    return "\n".join(line.strip() for line in norm_ws(s).split("\n"))


def find_span(text: str, old: str):
    """Gibt (start, end, strategie, treffer) zurueck. Nur erklaerbare Strategien."""
    n = text.count(old)
    if n == 1:
        i = text.index(old)
        return i, i + len(old), "exact", 1
    if n > 1:
        return None, None, "ambiguous-exact", n
    # zeilenweise, trailing whitespace ignoriert
    for strat, fn in (("line-trim", norm_ws), ("indent-trim", norm_indent)):
        nt, no = fn(text), fn(old)
        if no and nt.count(no) == 1:
            # Position in Originaltext ueber Zeilenindex rekonstruieren
            idx = nt.index(no)
            before_lines = nt[:idx].count("\n")
            lines_t = text.replace("\r\n", "\n").split("\n")
            lines_o = no.split("\n")
            start = sum(len(l) + 1 for l in lines_t[:before_lines])
            end = start + sum(len(l) + 1 for l in lines_o) - 1
            return start, end, strat, 1
        if no and nt.count(no) > 1:
            return None, None, strat + "-ambiguous", nt.count(no)
    return None, None, "not-found", 0


def apply_ops(ops, base_text, log):
    text = base_text
    warn = []
    for i, o in enumerate(ops):
        if o["op"] == "write":
            c = o.get("content")
            if c is None:
                log.append({"i": i, "ts": iso(o["ts"]), "op": "write", "status": "skip-content-missing"})
                warn.append("write ohne content")
                continue
            text = c
            log.append({"i": i, "ts": iso(o["ts"]), "op": "write", "status": "ok",
                        "len": len(c), "profile": o["profile"]})
        else:
            old, new = o.get("old_string"), o.get("new_string")
            if old is None or new is None:
                log.append({"i": i, "ts": iso(o["ts"]), "op": "patch", "status": "skip-args-missing"})
                warn.append("patch ohne old/new")
                continue
            n_expected = text.count(old)
            if o.get("replace_all"):
                if n_expected == 0:
                    s, e, strat, cnt = find_span(text, old)
                    if s is None:
                        log.append({"i": i, "ts": iso(o["ts"]), "op": "patch",
                                    "status": "not-applicable", "strategy": strat, "hits": cnt})
                        warn.append(f"patch {i} nicht anwendbar ({strat})")
                        continue
                    text = text[:s] + new + text[e:]
                else:
                    text = text.replace(old, new)
                log.append({"i": i, "ts": iso(o["ts"]), "op": "patch", "status": "ok",
                            "strategy": "replace_all", "profile": o["profile"]})
                continue
            s, e, strat, cnt = find_span(text, old)
            if s is None:
                log.append({"i": i, "ts": iso(o["ts"]), "op": "patch",
                            "status": "not-applicable", "strategy": strat, "hits": cnt})
                warn.append(f"patch {i} nicht anwendbar ({strat})")
                continue
            text = text[:s] + new + text[e:]
            log.append({"i": i, "ts": iso(o["ts"]), "op": "patch", "status": "ok",
                        "strategy": strat, "profile": o["profile"]})
    return text, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rel_path")
    ap.add_argument("--base-file", action="append", default=[])
    ap.add_argument("--compare", action="append", default=[])
    ap.add_argument("--after", default=None,
                    help="nur Operationen NACH diesem Zeitpunkt (ISO, z. B. 2026-10-07T00:48)")
    args = ap.parse_args()

    ops_all = [json.loads(l) for l in (WORK / "operations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ops = [o for o in ops_all if o["rel_path"] == args.rel_path]
    if args.after:
        cut = dt.datetime.fromisoformat(args.after).timestamp()
        ops = [o for o in ops if o["ts"] > cut]
    if not ops:
        print(f"keine Operationen fuer {args.rel_path}"
              + (f" nach {args.after}" if args.after else ""))
        return 0
    ops_ok = [o for o in ops if o["result"] == "ok"]
    ops_skip = [o for o in ops if o["result"] != "ok"]
    ops_ok.sort(key=lambda o: o["ts"])

    # Ketten nach Arbeitskopie trennen
    chains = {}
    for o in ops_ok:
        chains.setdefault(o.get("worktree") or "main", []).append(o)

    slug = args.rel_path.replace("/", "_")
    outdir = WORK / "replay" / slug
    outdir.mkdir(parents=True, exist_ok=True)

    report = {"rel_path": args.rel_path, "ops_total": len(ops),
              "ops_ok": len(ops_ok), "ops_skipped": len(ops_skip),
              "chains": {}, "compare": []}

    for chain_name, chain in chains.items():
        chain.sort(key=lambda o: o["ts"])
        first = chain[0]
        # Basis bestimmen
        if args.base_file:
            base_bytes = pathlib.Path(args.base_file[0]).read_bytes()
            base_src = f"file:{args.base_file[0]}"
            base_text = base_bytes.decode("utf-8", "replace")
            applied = chain
            log = []
            text, warn = apply_ops(applied, base_text, log)
        elif first["op"] == "write" and first.get("content") is not None:
            # Der erste Write IST der Anfang dieser Kette
            base_src = f"chain-start write @ {iso(first['ts'])}"
            applied = chain
            log = []
            text, warn = apply_ops(applied, "", log)
        else:
            base_src = "UNBEKANNT - erste Op ist ein patch ohne Basis"
            applied, log, warn, text = [], [], ["keine Basis: erster Vorgang ist ein patch"], None

        res = None
        if text is not None:
            b = text.encode("utf-8")
            res = {"bytes": len(b), "sha256": sha(b)}
            (outdir / f"{chain_name}.reconstructed").write_bytes(b)

        n_not = sum(1 for l in log if l.get("status") in ("not-applicable", "skip-args-missing", "skip-content-missing"))
        report["chains"][chain_name] = {
            "first": iso(chain[0]["ts"]), "last": iso(chain[-1]["ts"]),
            "n_ops_applied": len(applied), "base_source": base_src,
            "result": res, "problems": n_not, "warnings": warn[:20],
            "result_kind": "full" if n_not == 0 else "partial",
        }
        (outdir / f"{chain_name}.steps.json").write_text(
            json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    # Vergleich gegen Kandidaten
    for c in args.compare:
        p = pathlib.Path(c)
        if p.is_file():
            b = p.read_bytes()
            report["compare"].append({"path": c, "bytes": len(b), "sha256": sha(b),
                                      "mtime": dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")})

    (outdir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"# replay {args.rel_path}")
    print(f"Ops gesamt {len(ops)} | ok {len(ops_ok)} | uebersprungen (error) {len(ops_skip)}")
    for name, c in report["chains"].items():
        r = c["result"]
        print(f"\nKette '{name}'  {c['first']} -> {c['last']}  ({c['n_ops_applied']} Ops)")
        print(f"  Basis: {c['base_source']}")
        if r:
            print(f"  Ergebnis: {r['bytes']} B  sha256 {r['sha256'][:16]}  [{c['result_kind']}]")
        else:
            print("  Ergebnis: KEINS (Basis fehlt)")
        if c["problems"]:
            print(f"  nicht anwendbare Schritte: {c['problems']}")
            for w in c["warnings"][:5]:
                print(f"    - {w}")
    if report["compare"]:
        print("\nVergleich:")
        for c in report["compare"]:
            print(f"  {c['bytes']:>8} B  {c['sha256'][:16]}  {c['mtime']}  {c['path']}")
    print(f"\nBericht: {outdir/'report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
