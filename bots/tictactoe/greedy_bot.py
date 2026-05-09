#!/usr/bin/env python3
"""
Greedy TicTacToe bot.

Strategy (priority order):
  1. Win immediately if possible.
  2. Block opponent's winning move.
  3. Take center if free.
  4. Take a corner if free.
  5. Take any remaining cell.
"""
import json
import random
import sys


LINES = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
]

CORNERS = [{"row": 0, "col": 0}, {"row": 0, "col": 2},
           {"row": 2, "col": 0}, {"row": 2, "col": 2}]
CENTER = {"row": 1, "col": 1}


def find_winning_move(board, mark, valid_moves):
    """Return a move that immediately wins for `mark`, or None."""
    for move in valid_moves:
        r, c = move["row"], move["col"]
        board[r][c] = mark
        win = any(
            all(board[lr][lc] == mark for lr, lc in line)
            for line in LINES
        )
        board[r][c] = 0
        if win:
            return move
    return None


def choose_move(state, valid_moves, player):
    board = [row[:] for row in state["board"]]
    my_mark = player + 1
    opp_mark = 3 - my_mark

    # 1. Win
    move = find_winning_move(board, my_mark, valid_moves)
    if move:
        return move

    # 2. Block
    move = find_winning_move(board, opp_mark, valid_moves)
    if move:
        return move

    # 3. Center
    if CENTER in valid_moves:
        return CENTER

    # 4. Corner
    corners = [c for c in CORNERS if c in valid_moves]
    if corners:
        return random.choice(corners)

    # 5. Any
    return random.choice(valid_moves)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            move = choose_move(req["state"], req["valid_moves"], req["player"])
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
