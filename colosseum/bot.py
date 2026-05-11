import json
import shlex
import subprocess
from typing import Optional


class BotError(Exception):
    """Raised when a bot violates the protocol (timeout, bad JSON, crash)."""


class Bot:
    """
    Wrapper around an external bot process communicating over stdin/stdout.

    The bot process is started once and kept alive for the entire match.
    On each turn the runner sends one JSON line and expects one JSON line back.

    Protocol (runner -> bot):
        {"step": 5, "player": 1, "state": {...}, "valid_moves": [...]}

    Protocol (bot -> runner):
        {"move": {...}}
    """

    def __init__(self, name: str, command: str, timeout: float = 5.0) -> None:
        self.name = name
        self.command = command
        self.timeout = timeout
        self._process: Optional[subprocess.Popen] = None

    def start(self) -> None:
        """Launch the bot subprocess."""
        args = shlex.split(self.command)
        self._process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,  # line-buffered
        )

    def get_move(self, step: int, player: int, state: dict, valid_moves: list) -> dict:
        """
        Send game state to the bot and return its chosen move.

        Raises BotError on timeout, malformed response, or process crash.
        """
        if self._process is None:
            raise BotError(f"Bot '{self.name}' has not been started.")
        if self._process.poll() is not None:
            raise BotError(f"Bot '{self.name}' process has exited unexpectedly.")

        message = json.dumps(
            {"step": step, "player": player, "state": state, "valid_moves": valid_moves},
            ensure_ascii=False,
        )

        try:
            self._process.stdin.write(message + "\n")
            self._process.stdin.flush()
        except BrokenPipeError as e:
            raise BotError(f"Bot '{self.name}' stdin closed: {e}") from e

        try:
            line = self._readline_timeout()
        except TimeoutError:
            raise BotError(
                f"Bot '{self.name}' did not respond within {self.timeout}s."
            )

        if not line:
            raise BotError(f"Bot '{self.name}' returned empty response.")

        try:
            response = json.loads(line)
        except json.JSONDecodeError as e:
            raise BotError(f"Bot '{self.name}' returned invalid JSON: {e}") from e

        if "move" not in response:
            raise BotError(
                f"Bot '{self.name}' response missing 'move' key: {response}"
            )

        return response["move"]

    def _readline_timeout(self) -> str:
        """Read one line from stdout with a timeout."""
        import threading

        result: list = []
        error: list = []

        def _read():
            try:
                line = self._process.stdout.readline()
                result.append(line)
            except Exception as e:
                error.append(e)

        thread = threading.Thread(target=_read, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            raise TimeoutError()
        if error:
            raise BotError(f"Bot '{self.name}' read error: {error[0]}")
        return result[0].strip() if result else ""

    def close(self) -> None:
        """Terminate the bot process."""
        if self._process and self._process.poll() is None:
            try:
                self._process.stdin.close()
            except Exception:
                pass
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()

    def __repr__(self) -> str:
        return f"Bot(name={self.name!r}, command={self.command!r})"
