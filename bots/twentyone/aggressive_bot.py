#!/usr/bin/env python3
"""
Aggressive 21 bot.

Always hits until reaching 21 or busting. Never stands voluntarily.
Maximum risk, maximum reward.
"""
import json
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            actions = {m["action"] for m in req["valid_moves"]}
            # Always hit if possible, stand only when forced
            move = {"action": "hit"} if "hit" in actions else {"action": "stand"}
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
