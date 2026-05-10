#!/usr/bin/env python3
"""
Endgame Nim bot.

Plays randomly while the total number of stones is above a threshold,
then switches to the optimal XOR (Sprague-Grundy) strategy in the endgame.

This mimics a player who "wakes up" and starts playing seriously
only when the stakes become obvious.
"""
import json
import random
import sys

ENDGAME_THRESHOLD = 6  # switch to optimal when total stones <= this


def nim_xor_move(piles):
    """Return the optimal move, or take 1 from the largest if in a losing position."""
    nim_sum = 0
    for p in piles:
        nim_sum ^= p

    if nim_sum != 0:
        for i, size in enumerate(piles):
            target = size ^ nim_sum
            if target < size:
                return {"pile": i, "count": size - target}

    # Losing position — delay
    largest = max(range(len(piles)), key=lambda i: piles[i])
    return {"pile": largest, "count": 1}


def choose_move(piles, valid_moves):
    total = sum(piles)
    if total <= ENDGAME_THRESHOLD:
        return nim_xor_move(piles)
    return random.choice(valid_moves)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            move = choose_move(req["state"]["piles"], req["valid_moves"])
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
