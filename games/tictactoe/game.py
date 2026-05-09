import copy
from colosseum.game import Game

# Symbols for display
_SYMBOLS = {0: ".", 1: "X", 2: "O"}


class TicTacToe(Game):
    """
    Classic 3x3 Tic-Tac-Toe.

    State schema:
        {
            "board": [[int, int, int], [int, int, int], [int, int, int]],
            "current_player": int  # 0 or 1
        }
        Cell values: 0 = empty, 1 = player 0's mark (X), 2 = player 1's mark (O)

    Move schema:
        {"row": int, "col": int}  # 0-indexed
    """

    @property
    def num_players(self) -> int:
        return 2

    def initial_state(self) -> dict:
        return {
            "board": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "current_player": 0,
        }

    def valid_moves(self, state: dict) -> list:
        board = state["board"]
        return [
            {"row": r, "col": c}
            for r in range(3)
            for c in range(3)
            if board[r][c] == 0
        ]

    def apply_move(self, state: dict, move: dict) -> dict:
        new_state = copy.deepcopy(state)
        player = new_state["current_player"]
        mark = player + 1  # player 0 → 1 (X), player 1 → 2 (O)
        new_state["board"][move["row"]][move["col"]] = mark
        new_state["current_player"] = 1 - player
        return new_state

    def is_terminal(self, state: dict) -> bool:
        return self._winner(state) is not None or not self.valid_moves(state)

    def get_result(self, state: dict) -> dict:
        winner_mark = self._winner(state)
        if winner_mark is None:
            # Draw
            return {0: 0.5, 1: 0.5}
        winner_player = winner_mark - 1
        return {winner_player: 1.0, 1 - winner_player: 0.0}

    def render(self, state: dict) -> str:
        board = state["board"]
        rows = []
        for r in range(3):
            rows.append(" ".join(_SYMBOLS[board[r][c]] for c in range(3)))
        return "\n".join(rows)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _winner(self, state: dict) -> int | None:
        """Return the winning mark (1 or 2), or None if no winner yet."""
        board = state["board"]
        lines = [
            # rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
        for line in lines:
            values = [board[r][c] for r, c in line]
            if values[0] != 0 and values[0] == values[1] == values[2]:
                return values[0]
        return None
