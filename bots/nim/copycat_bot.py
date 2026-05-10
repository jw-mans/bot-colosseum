#!/usr/bin/env python3
"""
Copycat Nim bot.

Mirrors the opponent's last move (same pile index, same count) if possible.
Infers the opponent's move by comparing current piles with the state
after our own last move (tracked internally between turns).

Fallback when mirroring is impossible: take 1 from the largest pile.
"""
import json
import sys


def choose_move(piles, prev_piles):
    """
    piles:      current pile sizes (after opponent moved)
    prev_piles: pile sizes just after our own last move (before opponent moved)
                None on the first turn.
    """
    if prev_piles is not None:
        # Infer opponent's move
        for i, (old, new) in enumerate(zip(prev_piles, piles)):
            if old != new:
                count = old - new
                # Mirror: same pile, same count (if enough stones remain)
                if piles[i] >= count:
                    return {"pile": i, "count": count}
                break  # can't mirror, fall through to fallback

    # Fallback: take 1 from the largest pile
    largest = max(range(len(piles)), key=lambda i: piles[i])
    return {"pile": largest, "count": 1}


def main():
    prev_piles = None  # pile state just after our own last move

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            piles = req["state"]["piles"]

            move = choose_move(piles, prev_piles)

            # Record what piles will look like after our move
            prev_piles = piles[:]
            prev_piles[move["pile"]] -= move["count"]

            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
