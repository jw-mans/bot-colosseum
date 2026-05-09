from abc import ABC, abstractmethod


class Game(ABC):
    """Abstract base class for all games in the colosseum."""

    @property
    @abstractmethod
    def num_players(self) -> int:
        """Number of players in this game."""
        ...

    @abstractmethod
    def initial_state(self) -> dict:
        """Return the initial game state as a JSON-serializable dict."""
        ...

    @abstractmethod
    def valid_moves(self, state: dict) -> list:
        """Return list of valid moves for the current player in the given state."""
        ...

    @abstractmethod
    def apply_move(self, state: dict, move: dict) -> dict:
        """Apply a move to the state and return the new state. Must not mutate the input."""
        ...

    @abstractmethod
    def is_terminal(self, state: dict) -> bool:
        """Return True if the game is over."""
        ...

    @abstractmethod
    def get_result(self, state: dict) -> dict:
        """
        Return scores for each player.
        Keys are player indices (0-based), values are floats:
          1.0 = win, 0.5 = draw, 0.0 = loss
        Only call on a terminal state.
        """
        ...

    @abstractmethod
    def render(self, state: dict) -> str:
        """Return a human-readable string representation of the state."""
        ...
