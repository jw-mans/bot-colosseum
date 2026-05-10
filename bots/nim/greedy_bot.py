#!/usr/bin/env python3
"""
Greedy Nim bot.

Always takes the maximum number of stones from the largest pile.
Aggressive — tries to clear big piles as fast as possible.
"""
import json
import sys


def choose_move(piles):
    largest = max(range(len(piles)), key=lambda i: piles[i])
    return {"pile": largest, "count": piles[largest]}


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
