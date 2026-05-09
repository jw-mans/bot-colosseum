#!/usr/bin/env python3
"""
CLI entry point for running a single match between two bots.

Usage:
    python run_match.py --game tictactoe \
        --bot1 "python bots/random_bot.py" \
        --bot2 "python bots/random_bot.py" \
        [--timeout 5.0] \
        [--output matches/] \
        [--quiet]
"""
import argparse
import importlib
import sys
from pathlib import Path

from colosseum.bot import Bot
from colosseum.runner import MatchRunner

GAME_REGISTRY = {
    "tictactoe": "games.tictactoe.game.TicTacToe",
}


def load_game(name: str):
    if name not in GAME_REGISTRY:
        print(f"Unknown game '{name}'. Available: {', '.join(GAME_REGISTRY)}")
        sys.exit(1)
    module_path, class_name = GAME_REGISTRY[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()


def main():
    parser = argparse.ArgumentParser(description="Run a bot match in the colosseum.")
    parser.add_argument("--game", required=True, help="Game name (e.g. tictactoe)")
    parser.add_argument("--bot1", required=True, help="Command to launch bot 1")
    parser.add_argument("--bot2", required=True, help="Command to launch bot 2")
    parser.add_argument("--timeout", type=float, default=5.0, help="Move timeout in seconds")
    parser.add_argument("--output", default="matches", help="Directory to save match data")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-step output")
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()
