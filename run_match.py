#!/usr/bin/env python3
"""
CLI entry point for running matches between two bots.

Usage:
    colosseum --game tictactoe --bot1 "..." --bot2 "..."
    colosseum --game 21 --bot1 "..." --bot2 "..." --rounds 100
"""
import argparse
import importlib
import sys
from pathlib import Path

from colosseum.bot import Bot
from colosseum.runner import MatchRunner

GAME_REGISTRY = {
    "tictactoe": "games.tictactoe.game.TicTacToe",
    "nim":       "games.nim.game.Nim",
    "21":        "games.twentyone.game.TwentyOne",
}


def load_game(name: str):
    if name not in GAME_REGISTRY:
        print(f"Unknown game '{name}'. Available: {', '.join(GAME_REGISTRY)}")
        sys.exit(1)
    module_path, class_name = GAME_REGISTRY[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()


def print_stats(bot1_cmd: str, bot2_cmd: str, wins: list, draws: int,
                forfeits: int, total_steps: int, rounds: int) -> None:
    w1, w2 = wins
    pct = lambda n: f"{100 * n / rounds:.1f}%"

    print(f"\n{'=' * 60}")
    print(f"  Results: {rounds} rounds")
    print(f"{'=' * 60}")
    print(f"  Bot1 ({bot1_cmd[:35]}):  wins {w1:>4}  ({pct(w1)})")
    print(f"  Bot2 ({bot2_cmd[:35]}):  wins {w2:>4}  ({pct(w2)})")
    print(f"  Draws:                     {draws:>4}  ({pct(draws)})")
    if forfeits:
        print(f"  Forfeits:                  {forfeits:>4}  ({pct(forfeits)})")
    print(f"  Avg steps per round:      {total_steps / rounds:>5.1f}")
    print(f"{'=' * 60}")


def run_single(args) -> None:
    game = load_game(args.game)
    bots = [
        Bot(name="bot1", command=args.bot1, timeout=args.timeout),
        Bot(name="bot2", command=args.bot2, timeout=args.timeout),
    ]
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    runner = MatchRunner(verbose=not args.quiet)
    print(f"Match: {args.game}  |  {args.bot1!r} vs {args.bot2!r}")
    print("-" * 60)

    result = runner.run(game, bots, output_dir)
    print(f"\nSaved to: {result.match_dir}")


def run_multi(args) -> None:
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    runner = MatchRunner(verbose=False)

    wins = [0, 0]
    draws = 0
    forfeits = 0
    total_steps = 0

    print(f"Match: {args.game}  |  {args.bot1!r} vs {args.bot2!r}")
    print(f"Rounds: {args.rounds}")
    print("-" * 60)

    for i in range(args.rounds):
        print(f"\r[{i + 1}/{args.rounds}]", end="", flush=True)

        game = load_game(args.game)
        bots = [
            Bot(name="bot1", command=args.bot1, timeout=args.timeout),
            Bot(name="bot2", command=args.bot2, timeout=args.timeout),
        ]
        result = runner.run(game, bots, output_dir)

        total_steps += result.total_steps
        if result.forfeit:
            forfeits += 1
            winner = 1 - result.forfeit_player
            wins[winner] += 1
        elif result.winner is None:
            draws += 1
        else:
            wins[result.winner] += 1

    print()  # новая строка после прогресса
    print_stats(args.bot1, args.bot2, wins, draws, forfeits, total_steps, args.rounds)


def main():
    parser = argparse.ArgumentParser(description="Run bot matches in the colosseum.")
    parser.add_argument("--game",    required=True,           help="Game name (e.g. tictactoe)")
    parser.add_argument("--bot1",    required=True,           help="Command to launch bot 1")
    parser.add_argument("--bot2",    required=True,           help="Command to launch bot 2")
    parser.add_argument("--rounds",  type=int,  default=1,   help="Number of rounds to play (default: 1)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Move timeout in seconds (default: 5.0)")
    parser.add_argument("--output",  default="matches",       help="Directory to save match data (default: matches/)")
    parser.add_argument("--quiet",   action="store_true",     help="Suppress per-step output (single round only)")
    args = parser.parse_args()

    if args.rounds == 1:
        run_single(args)
    else:
        run_multi(args)


if __name__ == "__main__":
    main()
