import copy
import random
from colosseum.game import Game

# Standard 52-card deck: 2-9 face value, 10/J/Q/K = 10, A = 11
_DECK = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4


def hand_value(cards: list) -> int:
    """Compute best hand value, counting aces as 1 when needed."""
    total = sum(cards)
    aces = cards.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


class TwentyOne(Game):
    """
    Simplified 21 (Score / Blackjack).

    Both players receive 2 cards at game start. Players alternate turns:
    on each turn a player may hit (draw one card) or stand (stop drawing).
    If a player's hand exceeds 21 they bust and are immediately done.
    If a player reaches exactly 21 they are immediately done.
    The player closest to 21 without busting wins.

    State schema:
        {
            "hands":  [[int, ...], [int, ...]],  # cards for each player
            "deck":   [int, ...],                # remaining draw pile
            "done":   [bool, bool],              # stood or busted?
            "current_player": int
        }
    Card values: 2-9 face value, 10/J/Q/K = 10, A = 11 (auto-reduced to 1).

    Move schema:
        {"action": "hit"}   — draw one card
        {"action": "stand"} — stop drawing
    """

    @property
    def num_players(self) -> int:
        return 2

    def initial_state(self) -> dict:
        deck = _DECK[:]
        random.shuffle(deck)
        hands: list = [[], []]
        for _ in range(2):
            for p in range(2):
                hands[p].append(deck.pop())
        return {
            "hands": hands,
            "deck": deck,
            "done": [False, False],
            "current_player": 0,
        }

    def valid_moves(self, state: dict) -> list:
        player = state["current_player"]
        value = hand_value(state["hands"][player])
        if value >= 21 or not state["deck"]:
            return [{"action": "stand"}]
        return [{"action": "hit"}, {"action": "stand"}]

    def apply_move(self, state: dict, move: dict) -> dict:
        new_state = copy.deepcopy(state)
        player = new_state["current_player"]

        if move["action"] == "hit":
            card = new_state["deck"].pop()
            new_state["hands"][player].append(card)
            if hand_value(new_state["hands"][player]) >= 21:
                new_state["done"][player] = True
        else:  # stand
            new_state["done"][player] = True

        # Switch to the other player if they're not done yet
        other = 1 - player
        if new_state["done"][player] and not new_state["done"][other]:
            new_state["current_player"] = other

        return new_state

    def is_terminal(self, state: dict) -> bool:
        return all(state["done"])

    def get_result(self, state: dict) -> dict:
        values = [hand_value(state["hands"][p]) for p in range(2)]
        busted = [v > 21 for v in values]

        if busted[0] and busted[1]:
            return {0: 0.5, 1: 0.5}
        if busted[0]:
            return {0: 0.0, 1: 1.0}
        if busted[1]:
            return {0: 1.0, 1: 0.0}

        if values[0] > values[1]:
            return {0: 1.0, 1: 0.0}
        if values[1] > values[0]:
            return {0: 0.0, 1: 1.0}
        return {0: 0.5, 1: 0.5}

    def render(self, state: dict) -> str:
        lines = []
        for p in range(2):
            hand = state["hands"][p]
            value = hand_value(hand)
            if value > 21:
                status = "BUST"
            elif state["done"][p]:
                status = "stood"
            else:
                status = "playing"
            lines.append(f"  Player {p}: {hand} = {value}  [{status}]")
        lines.append(f"  Deck: {len(state['deck'])} cards remaining")
        return "\n".join(lines)
