"""
Loop engineering tool for opencode — session search and recent-session listing.

Searches the opencode SQLite DB (session / message / part tables) to find
user corrections, skill gaps, and good techniques across sessions.

Usage:
    py script/loop.py <query> [--limit N] [--title-only]
    py script/loop.py "OKF" --limit 5
    py script/loop.py --recent 7     # list sessions updated in last 7 days
    py script/loop.py --version      # show version
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

DB_PATH = os.path.expandvars(r"%USERPROFILE%\.local\share\opencode\opencode.db")
__version__ = "1.0.0"


def _ts_to_str(ts: int) -> str:
    try:
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError, OverflowError):
        return "?"


def _extract_text(data: str) -> str:
    """Extract readable text from part.data / message.data JSON."""
    try:
        obj = json.loads(data)
    except json.JSONDecodeError:
        return data or ""

    if isinstance(obj, dict) and isinstance(obj.get("parts"), list):
        texts = []
        for p in obj["parts"]:
            t = _part_text(p)
            if t:
                texts.append(t)
        return "\n".join(texts)

    if isinstance(obj, dict):
        return _part_text(obj)

    return ""


def _part_text(p) -> str:
    if isinstance(p, str):
        return p
    if not isinstance(p, dict):
        return ""
    t = p.get("type", "")
    if t == "text":
        return p.get("text", "")
    if t == "tool":
        state = p.get("state", {})
        inp = state.get("input", {}) if isinstance(state, dict) else {}
        if isinstance(inp, dict):
            return f"[tool:{p.get('tool','')}] {json.dumps(inp, ensure_ascii=False)[:300]}"
        return f"[tool:{p.get('tool','')}] {str(inp)[:300]}"
    if t == "reasoning":
        return f"[reasoning] {p.get('text','')[:300]}"
    return json.dumps(p, ensure_ascii=False)[:300]


def search_sessions(query: str, limit: int = 20, title_only: bool = False) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    results = []
    seen: set[str] = set()

    try:
        if title_only:
            rows = conn.execute(
                "SELECT id, title, directory, time_updated, time_created "
                "FROM session WHERE title LIKE ? "
                "ORDER BY time_updated DESC LIMIT ?",
                (f"%{query}%", limit),
            ).fetchall()
            for r in rows:
                results.append({
                    "session_id": r["id"],
                    "title": r["title"],
                    "directory": r["directory"],
                    "time_updated": _ts_to_str(r["time_updated"]),
                    "matched_in": "title",
                    "snippet": "",
                })
        else:
            part_rows = conn.execute(
                "SELECT p.session_id, s.title, s.directory, s.time_updated, p.data "
                "FROM part p JOIN session s ON s.id = p.session_id "
                "WHERE p.data LIKE ? ORDER BY s.time_updated DESC",
                (f"%{query}%",),
            ).fetchall()
            for r in part_rows:
                if r["session_id"] in seen:
                    continue
                seen.add(r["session_id"])
                snippet = _extract_text(r["data"])
                results.append({
                    "session_id": r["session_id"],
                    "title": r["title"],
                    "directory": r["directory"],
                    "time_updated": _ts_to_str(r["time_updated"]),
                    "matched_in": "part",
                    "snippet": snippet[:300],
                })
                if len(results) >= limit:
                    break

            if len(results) < limit:
                msg_rows = conn.execute(
                    "SELECT m.session_id, s.title, s.directory, s.time_updated, m.data "
                    "FROM message m JOIN session s ON s.id = m.session_id "
                    "WHERE m.data LIKE ? ORDER BY s.time_updated DESC",
                    (f"%{query}%",),
                ).fetchall()
                for r in msg_rows:
                    if r["session_id"] in seen:
                        continue
                    seen.add(r["session_id"])
                    results.append({
                        "session_id": r["session_id"],
                        "title": r["title"],
                        "directory": r["directory"],
                        "time_updated": _ts_to_str(r["time_updated"]),
                        "matched_in": "message",
                        "snippet": _extract_text(r["data"])[:300],
                    })
                    if len(results) >= limit:
                        break
    finally:
        conn.close()

    return results


def list_recent_sessions(days: int, limit: int = 20,
                         dir_filter: str | None = None,
                         compact: bool = False) -> list[dict]:
    """List sessions updated in the last N days (newest first).

    Used by loop engineering to review recent sessions beyond the current one.
    Fetches latest messages from part table and returns title-based summary.
    compact=True returns title only (one line per session).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    since_ms = int((datetime.now(timezone.utc).timestamp() - days * 86400) * 1000)
    results = []

    try:
        if dir_filter:
            rows = conn.execute(
                "SELECT id, title, directory, time_updated, time_created "
                "FROM session WHERE time_updated >= ? AND directory LIKE ? "
                "ORDER BY time_updated DESC LIMIT ?",
                (since_ms, f"%{dir_filter}%", limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, directory, time_updated, time_created "
                "FROM session WHERE time_updated >= ? "
                "ORDER BY time_updated DESC LIMIT ?",
                (since_ms, limit),
            ).fetchall()
        for r in rows:
            if compact:
                results.append({
                    "session_id": r["id"],
                    "title": r["title"] or "(untitled)",
                    "directory": r["directory"],
                    "time_updated": _ts_to_str(r["time_updated"]),
                    "last_parts": [],
                })
                continue
            parts = conn.execute(
                "SELECT data FROM part WHERE session_id = ? "
                "ORDER BY rowid DESC LIMIT 3",
                (r["id"],),
            ).fetchall()
            recent = []
            for p in reversed(parts):
                t = _extract_text(p["data"])
                if t:
                    recent.append(t[:200])
            results.append({
                "session_id": r["id"],
                "title": r["title"] or "(untitled)",
                "directory": r["directory"],
                "time_updated": _ts_to_str(r["time_updated"]),
                "last_parts": recent,
            })
    finally:
        conn.close()

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="opencode session content search for loop engineering")
    parser.add_argument("query", nargs="?", default=None, help="search query")
    parser.add_argument("--limit", type=int, default=20, help="max results (default: 20)")
    parser.add_argument("--title-only", action="store_true", help="search titles only")
    parser.add_argument("--recent", type=int, default=0,
                        help="list sessions updated in last N days (no query needed)")
    parser.add_argument("--dir", dest="dir_filter", default=None,
                        help="--recent: filter by directory name substring (e.g. support-tool)")
    parser.add_argument("--compact", action="store_true",
                        help="--recent: show title only (no last_parts)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        return 1

    if args.recent:
        sessions = list_recent_sessions(args.recent, limit=args.limit,
                                        dir_filter=args.dir_filter,
                                        compact=args.compact)
        if not sessions:
            print(f"0 sessions updated in the last {args.recent} days"
                  + (f" (dir filter: {args.dir_filter})" if args.dir_filter else ""))
            return 0
        if args.compact:
            print(f"{len(sessions)} sessions updated in the last {args.recent} days:\n")
            for i, s in enumerate(sessions, 1):
                print(f"[{i}] {s['time_updated']}  {s['title']}  ({s['directory']})")
            return 0
        print(f"{len(sessions)} sessions updated in the last {args.recent} days:\n")
        for i, s in enumerate(sessions, 1):
            print(f"[{i}] {s['time_updated']}  {s['title']}")
            print(f"    session: {s['session_id']}")
            print(f"    dir:     {s['directory']}")
            for t in s["last_parts"]:
                print(f"    > {t.replace(chr(10), ' ')}")
            print()
        return 0

    if not args.query:
        print("error: query is required (or use --recent N)")
        return 1

    results = search_sessions(args.query, limit=args.limit, title_only=args.title_only)

    if not results:
        print(f"0 results for '{args.query}'")
        return 0

    print(f"{len(results)} results for '{args.query}':\n")
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['time_updated']}  {r['title']}")
        print(f"    session: {r['session_id']}")
        print(f"    dir:     {r['directory']}")
        print(f"    matched: {r['matched_in']}")
        if r["snippet"]:
            print(f"    snippet: {r['snippet'].replace(chr(10), ' ')}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
