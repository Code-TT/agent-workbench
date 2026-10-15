"""CLI: python -m testslot_manager <acquire|status|heartbeat|release|start|restart|stop|logs|db-refresh|db-backup> ...

Alle schreibenden Kommandos verlangen --token nach acquire. Keine echten
npm/DB/Cloud-Aktionen; Prozesse laufen auf loopback.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import manager as m


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="testslot_manager",
                                description="Manager fuer 4 logische Testplaetze (anbieterneutral)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("acquire"); a.add_argument("--owner", required=True); a.add_argument("--slot", type=int)
    sub.add_parser("status")
    h = sub.add_parser("heartbeat"); h.add_argument("--slot", type=int, required=True); h.add_argument("--token", required=True)
    r = sub.add_parser("release"); r.add_argument("--slot", type=int, required=True); r.add_argument("--token", required=True)
    r.add_argument("--keep-process", action="store_true", help="Prozess NICHT stoppen (nur Lease loesen)")
    s = sub.add_parser("start"); s.add_argument("--slot", type=int, required=True); s.add_argument("--token", required=True)
    s.add_argument("--port", type=int); s.add_argument("--health-timeout", type=float, default=30.0)
    s.add_argument("--", dest="extra", help="Eigenes Kommando ab hier", nargs=argparse.REMAINDER)
    rs = sub.add_parser("restart"); rs.add_argument("--slot", type=int, required=True); rs.add_argument("--token", required=True)
    rs.add_argument("--attempts", type=int, default=2)
    st = sub.add_parser("stop"); st.add_argument("--slot", type=int, required=True); st.add_argument("--token", required=True)
    lg = sub.add_parser("logs"); lg.add_argument("--slot", type=int, required=True); lg.add_argument("--tail", type=int, default=50)
    sub.add_parser("db-refresh"); sub.add_parser("db-backup")

    args = p.parse_args(argv)
    mgr = m.SlotManager()
    try:
        if args.cmd == "acquire":
            print(json.dumps(mgr.acquire(args.owner, args.slot), indent=2))
        elif args.cmd == "status":
            print(json.dumps(mgr.status(), indent=2))
        elif args.cmd == "heartbeat":
            print(json.dumps(mgr.heartbeat(args.slot, args.token), indent=2))
        elif args.cmd == "release":
            print(json.dumps(mgr.release(args.slot, args.token, stop_process=not args.keep_process), indent=2))
        elif args.cmd == "start":
            print(json.dumps(mgr.start(args.slot, args.token, command=args.extra,
                                       port=args.port, health_timeout=args.health_timeout), indent=2))
        elif args.cmd == "restart":
            print(json.dumps(mgr.restart(args.slot, args.token, max_attempts=args.attempts), indent=2))
        elif args.cmd == "stop":
            print(json.dumps(mgr.stop(args.slot, args.token), indent=2))
        elif args.cmd == "logs":
            print(mgr.logs(args.slot, tail=args.tail))
        elif args.cmd == "db-refresh":
            m.db_refresh()
        elif args.cmd == "db-backup":
            m.db_backup()
    except (m.SlotError, m.DbRefreshUnavailable, m.DbBackupUnavailable) as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
