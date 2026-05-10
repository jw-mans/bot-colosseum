#!/usr/bin/env python3
"""
Optimal Nim bot using the Sprague-Grundy / nim-sum strategy.

Theory:
  nim_sum = XOR of all pile sizes.
  - If nim_sum == 0: current position is a loss with perfect play.
    Nothing to do — play any move (here: take 1 from the largest pile).
  - If nim_sum != 0: a winning move exists.
    Find pile i where piles[i] XOR nim_sum < piles[i],
    then reduce that pile to (piles[i] XOR nim_sum).
    This makes nim_sum == 0 for the opponent.
"""
import json
import sys


def choose_move(piles, valid_moves):
    nim_sum = 0
    for p in piles:
        nim_sum ^= p

    if nim_sum != 0:
        # Winning position: find the move that sets nim_sum to 0
        for i, size in enumerate(piles):
            target = size ^ nim_sum
            if target < size:
                count = size - target
                return {"pile": i, "count": count}

    # Losing position: take 1 from the largest pile (delay the inevitable)
    largest = max(range(len(piles)), key=lambda i: piles[i])
    return {"pile": largest, "count": 1}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            piles = req["state"]["piles"]
            move = choose_move(piles, req["valid_moves"])
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
