#!/usr/bin/env python3
"""
Minimax TicTacToe bot.

Plays perfectly — never loses. Uses minimax with alpha-beta pruning.
On 3x3 board the search space is tiny (~9! = 362880 nodes max),
so alpha-beta is instant but included for correctness.
"""
import json
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


def check_winner(board):
    """Return winning mark (1 or 2) or None."""
    for line in LINES:
        vals = [board[r][c] for r, c in line]
        if vals[0] != 0 and vals[0] == vals[1] == vals[2]:
            return vals[0]
    return None


def is_full(board):
    return all(board[r][c] != 0 for r in range(3) for c in range(3))


def minimax(board, my_mark, opp_mark, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner == my_mark:
        return 1
    if winner == opp_mark:
        return -1
    if is_full(board):
        return 0

    if is_maximizing:
        best = -2
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = my_mark
                    score = minimax(board, my_mark, opp_mark, False, alpha, beta)
                    board[r][c] = 0
                    best = max(best, score)
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        return best
        return best
    else:
        best = 2
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = opp_mark
                    score = minimax(board, my_mark, opp_mark, True, alpha, beta)
                    board[r][c] = 0
                    best = min(best, score)
                    beta = min(beta, best)
                    if beta <= alpha:
                        return best
        return best


def best_move(state, player):
    board = [row[:] for row in state["board"]]
    my_mark = player + 1
    opp_mark = 3 - my_mark

    best_score = -2
    chosen = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                board[r][c] = my_mark
                score = minimax(board, my_mark, opp_mark, False, -2, 2)
                board[r][c] = 0
                if score > best_score:
                    best_score = score
                    chosen = {"row": r, "col": c}
    return chosen


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            move = best_move(req["state"], req["player"])
            print(json.dumps({"move": move}), flush=True)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr, flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
