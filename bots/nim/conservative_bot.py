#!/usr/bin/env python3
"""
Conservative Nim bot.

Always takes exactly 1 stone from the largest non-empty pile.
Maximally slow — forces the game to last as long as possible.
"""
import json
import sys


def choose_move(piles):
    largest = max(range(len(piles)), key=lambda i: piles[i])
    return {"pile": largest, "count": 1}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            move = choose_move(req["state"]["piles"])
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
