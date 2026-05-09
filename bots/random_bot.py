#!/usr/bin/env python3
"""
Universal random bot.

Works with any game that follows the colosseum stdin/stdout protocol.
Reads a JSON line from stdin, picks a random move from valid_moves,
writes the response to stdout.

Protocol input:
    {"step": N, "player": N, "state": {...}, "valid_moves": [...]}

Protocol output:
    {"move": {...}}
"""
import json
import random
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            valid_moves = request["valid_moves"]
            move = random.choice(valid_moves)
            response = json.dumps({"move": move}, ensure_ascii=False)
            print(response, flush=True)
        except Exception as e:
            # Write error to stderr so it doesn't corrupt the protocol
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
