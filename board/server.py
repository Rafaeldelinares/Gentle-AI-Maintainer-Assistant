#!/usr/bin/env python3
"""
server.py — Entry point for the local board.

    python3 board/server.py                 # serves 127.0.0.1:8770
    python3 board/server.py --ingest        # refresh the projection, then serve
    python3 board/server.py --port 8780

Binds to 127.0.0.1 only: this is a local console, it must not be exposed on the LAN.
The port is deliberately not 8000, which the ByBusiness CRM cockpit already occupies.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402
import api  # noqa: E402

DEFAULT_PORT = 8770


def main():
    parser = argparse.ArgumentParser(description="Gentle AI Maintainer board (local, read-only toward GitHub)")
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port (default: {DEFAULT_PORT})")
    parser.add_argument("--ingest", action="store_true", help="rebuild the projection from issues.json before serving")
    args = parser.parse_args()

    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(f"refusing to bind {args.host}: this board must stay local", file=sys.stderr)
        return 2

    conn = core.connect()
    try:
        core.init_schema(conn)
        if args.ingest or conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"] == 0:
            stats = core.ingest(conn)
            print(f"[board] ingested {stats['cards']} cards from {stats['meta']['path']} "
                  f"(sha256 {stats['meta']['sha256']})")
        core.rebuild_state(conn)
        per_board = core.counts_by_slug(conn)
    finally:
        conn.close()

    for slug in sorted(per_board):
        print(f"[board] {slug}: {sum(per_board[slug].values())} cards")

    server = api.build_server(args.host, args.port)
    print(f"[board] serving http://{args.host}:{args.port}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[board] stopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
