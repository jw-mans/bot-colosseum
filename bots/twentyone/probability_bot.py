#!/usr/bin/env python3
"""
Probability 21 bot.

Calculates the exact bust probability from the remaining deck and hits
only when the probability of busting is below the threshold (default 40%).

Uses full information: knows which cards are left in the deck from the state.
"""
import json
import sys

BUST_THRESHOLD = 0.40  # hit if bust chance < 40%


def hand_value(cards):
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def bust_probability(hand, deck):
    """Fraction of remaining deck cards that would cause a bust."""
    if not deck:
        return 1.0
    current = hand_value(hand)
    bust_count = sum(1 for card in deck if hand_value(hand + [card]) > 21)
    return bust_count / len(deck)


def choose_action(state, player, valid_moves):
    actions = {m["action"] for m in valid_moves}
    if "hit" not in actions:
        return {"action": "stand"}

    hand = state["hands"][player]
    deck = state["deck"]
    p_bust = bust_probability(hand, deck)

    if p_bust < BUST_THRESHOLD:
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
