#!/usr/bin/env python3
"""
Counter 21 bot.

Adapts strategy based on the opponent's current state:
  - Opponent busted               → stand immediately (already winning)
  - Opponent stood and we're ahead → stand (lock in the win)
  - Opponent stood and we're behind or tied → hit (must catch up)
  - Opponent still playing        → cautious fallback (stand at 17+)
"""
import json
import sys

FALLBACK_THRESHOLD = 17  # used when opponent hasn't acted yet


def hand_value(cards):
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def choose_action(state, player, valid_moves):
    actions = {m["action"] for m in valid_moves}
    if "hit" not in actions:
        return {"action": "stand"}

    opponent = 1 - player
    my_value = hand_value(state["hands"][player])
    opp_value = hand_value(state["hands"][opponent])
    opp_done = state["done"][opponent]
    opp_busted = opp_done and opp_value > 21

    # Opponent already busted — any non-bust hand wins
    if opp_busted:
        return {"action": "stand"}

    # Opponent stood — we know their final score
    if opp_done:
        if my_value > opp_value:
            return {"action": "stand"}   # we're ahead, lock it in
        else:
            return {"action": "hit"}     # behind or tied, must try to beat them

    # Opponent still playing — use cautious fallback
    if my_value >= FALLBACK_THRESHOLD:
        return {"action": "stand"}
    return {"action": "hit"}


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
