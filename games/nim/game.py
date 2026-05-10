import copy
from colosseum.game import Game


class Nim(Game):
    """
    Classic Nim.

    Players take turns removing any positive number of stones from exactly
    one pile. The player who takes the last stone wins.

    State schema:
        {
            "piles": [int, ...],   # stone counts per pile
            "current_player": int
        }

    Move schema:
        {"pile": int, "count": int}   # remove `count` stones from pile `pile`
    """

    def __init__(self, piles: list = None) -> None:
        self._initial_piles = list(piles) if piles is not None else [3, 5, 7]

    @property
    def num_players(self) -> int:
        return 2

    def initial_state(self) -> dict:
        return {
            "piles": list(self._initial_piles),
            "current_player": 0,
        }

    def valid_moves(self, state: dict) -> list:
        moves = []
        for i, size in enumerate(state["piles"]):
            for n in range(1, size + 1):
                moves.append({"pile": i, "count": n})
        return moves

    def apply_move(self, state: dict, move: dict) -> dict:
        new_state = copy.deepcopy(state)
        new_state["piles"][move["pile"]] -= move["count"]
        new_state["current_player"] = 1 - state["current_player"]
        return new_state

    def is_terminal(self, state: dict) -> bool:
        return all(p == 0 for p in state["piles"])

    def get_result(self, state: dict) -> dict:
        # All piles are empty — the player who just moved took the last stone.
        # After apply_move the turn was already flipped, so current_player
        # is the one who did NOT take the last stone → loser.
        loser = state["current_player"]
        winner = 1 - loser
        return {winner: 1.0, loser: 0.0}

    def render(self, state: dict) -> str:
        lines = []
        for i, size in enumerate(state["piles"]):
            bar = "|" * size
            lines.append(f"  Pile {i}: {bar:<15} ({size})")
        return "\n".join(lines)
