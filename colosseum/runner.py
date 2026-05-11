import datetime
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from colosseum.bot import Bot, BotError
from colosseum.game import Game
from colosseum import persistence


@dataclass
class MatchResult:
    match_id: str
    scores: dict # {player_index: float}
    winner: Optional[int] # None = draw
    total_steps: int
    forfeit: bool = False
    forfeit_player: Optional[int] = None
    match_dir: Optional[Path] = None


class MatchRunner:
    """Orchestrates a single match between bots."""

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    def run(
        self,
        game: Game,
        bots: list[Bot],
        base_dir: Path,
    ) -> MatchResult:
        """
        Run a match to completion.

        Args:
            game:     Game instance.
            bots:     List of Bot instances, one per player (index matches player id).
            base_dir: Root directory where match data will be saved.

        Returns:
            MatchResult with scores, winner and location of saved data.
        """
        assert len(bots) == game.num_players, (
            f"Game requires {game.num_players} players, got {len(bots)} bots."
        )

        match_id = uuid.uuid4().hex
        meta = {
            "match_id": match_id,
            "game": type(game).__name__,
            "bots": [{"name": b.name, "command": b.command} for b in bots],
            "start_time": datetime.datetime.utcnow().isoformat() + "Z",
        }
        match_dir = persistence.init_match_dir(base_dir, match_id, meta)

        # Start all bot processes
        for bot in bots:
            bot.start()

        state = game.initial_state()
        step = 0
        forfeit = False
        forfeit_player = None

        try:
            while not game.is_terminal(state):
                current_player = state["current_player"]
                bot = bots[current_player]
                moves = game.valid_moves(state)

                # Ask bot for a move
                try:
                    move = bot.get_move(step, current_player, state, moves)
                except BotError as e:
                    self._log(f"[forfeit] Bot '{bot.name}' error: {e}")
                    forfeit = True
                    forfeit_player = current_player
                    break

                # Validate move
                if move not in moves:
                    self._log(
                        f"[forfeit] Bot '{bot.name}' returned invalid move: {move}"
                    )
                    forfeit = True
                    forfeit_player = current_player
                    break

                # Apply move
                state = game.apply_move(state, move)
                persistence.save_step(match_dir, step, current_player, move, state)

                if self.verbose:
                    self._log(
                        f"Step {step:3d} | Player {current_player} ({bot.name}) "
                        f"plays {move}"
                    )
                    self._log(game.render(state))

                step += 1

        finally:
            for bot in bots:
                bot.close()

        # Compute result
        if forfeit:
            # Forfeiting player loses, others win
            scores = {}
            for i in range(game.num_players):
                if i == forfeit_player:
                    scores[i] = 0.0
                else:
                    scores[i] = 1.0
            winner = next(
                (i for i in range(game.num_players) if i != forfeit_player), None
            )
        else:
            scores = game.get_result(state)
            max_score = max(scores.values())
            winners = [i for i, s in scores.items() if s == max_score]
            winner = winners[0] if len(winners) == 1 else None

        result_data = {
            "match_id": match_id,
            "scores": {str(k): v for k, v in scores.items()},
            "winner": winner,
            "total_steps": step,
            "forfeit": forfeit,
            "forfeit_player": forfeit_player,
        }
        persistence.save_result(match_dir, result_data)

        if self.verbose:
            self._print_summary(bots, winner, scores, forfeit, forfeit_player)

        return MatchResult(
            match_id=match_id,
            scores=scores,
            winner=winner,
            total_steps=step,
            forfeit=forfeit,
            forfeit_player=forfeit_player,
            match_dir=match_dir,
        )

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def _print_summary(
        self,
        bots: list[Bot],
        winner: Optional[int],
        scores: dict,
        forfeit: bool,
        forfeit_player: Optional[int],
    ) -> None:
        print("\n--- Result ---")
        for i, bot in enumerate(bots):
            score_str = f"{scores.get(i, 0.0):.1f}"
            print(f"  Player {i} ({bot.name}): {score_str}")
        if forfeit:
            print(f"  Forfeit by player {forfeit_player} ({bots[forfeit_player].name})")
        if winner is None:
            print("  Draw")
        else:
            print(f"  Winner: Player {winner} ({bots[winner].name})")
