#!/usr/bin/env python3
"""
Cautious 21 bot — classic dealer strategy.

Hits while hand value < 17, stands at 17 or above.
This mirrors the standard casino dealer rule.
"""
import json
import sys


def hand_value(cards):
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def choose_action(state, player, valid_moves):
    value = hand_value(state["hands"][player])
    actions = {m["action"] for m in valid_moves}
    if value < 17 and "hit" in actions:
        return {"action": "hit"}
    return {"action": "stand"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            move = choose_action(req["state"], req["player"], req["valid_moves"])
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
