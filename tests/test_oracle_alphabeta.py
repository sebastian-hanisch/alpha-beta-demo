"""Unabhängiges Orakel für Alpha-Beta: Spielwert, bester Zug und Knotenzahl.

Anderer Rechenweg als `ab_alphabeta`: Stellung als Spalten-Tupel, Siegprüfung durch
Aufzählen aller Viererlinien, exakte Spielwerte memoisiert (kein Pruning), und die
Alpha-Beta-Suche selbst als Negamax-Formulierung (statt Max-/Min-Zweig) mit eigener
Knotenzählung. Wert und gewählter Zug müssen exakt dem reinen Minimax-Wert
entsprechen, die Knotenzahl muss je Zugreihenfolge identisch sein.
"""

import random
from functools import lru_cache

import pytest

from ab_alphabeta import solve_position
from ab_constants import ORDER_BEST_CASE, ORDER_CENTER_FIRST, ORDER_NAIVE, ORDER_WORST_CASE
from ab_game import apply_move, check_win_at, empty_board, legal_columns

ORDERS = (ORDER_NAIVE, ORDER_CENTER_FIRST, ORDER_WORST_CASE, ORDER_BEST_CASE)


def _lines(rows, cols):
    out = []
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = [(r + i * dr, c + i * dc) for i in range(4)]
                if all(0 <= a < rows and 0 <= b < cols for a, b in cells):
                    out.append(cells)
    return out


class _Oracle:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.lines = _lines(rows, cols)
        self.exact = lru_cache(maxsize=None)(self._exact)

    def cell(self, st, r, c):
        h = self.rows - 1 - r
        return st[c][h] if h < len(st[c]) else 0

    def won(self, st, p):
        return any(all(self.cell(st, r, c) == p for r, c in line) for line in self.lines)

    def moves(self, st):
        return [c for c in range(self.cols) if len(st[c]) < self.rows]

    def play(self, st, c, p):
        return st[:c] + (st[c] + (p,),) + st[c + 1 :]

    def child(self, st, c, p):
        """Wert des Zuges c aus Sicht des Ziehenden p (+1 Sieg, 0 Remis, -1 Niederlage), exakt."""
        ns = self.play(st, c, p)
        if self.won(ns, p):
            return 1
        if not self.moves(ns):
            return 0
        return -self.exact(ns, 3 - p)

    def _exact(self, st, p):
        return max(self.child(st, c, p) for c in self.moves(st))

    def order(self, st, p, kind):
        cols = self.moves(st)
        if kind == ORDER_NAIVE:
            return cols
        if kind == ORDER_CENTER_FIRST:
            return sorted(cols, key=lambda c: (abs(2 * c - (self.cols - 1)), c))
        if kind == ORDER_BEST_CASE:
            return sorted(cols, key=lambda c: (-self.child(st, c, p), c))
        return sorted(cols, key=lambda c: (self.child(st, c, p), c))

    def negamax(self, st, p, a, b, kind, counter):
        counter[0] += 1
        best = -9
        for c in self.order(st, p, kind):
            ns = self.play(st, c, p)
            if self.won(ns, p):
                v = 1
            elif not self.moves(ns):
                v = 0
            else:
                v = -self.negamax(ns, 3 - p, -b, -a, kind, counter)
            best = max(best, v)
            a = max(a, best)
            if a >= b:
                break
        return best


def _to_state(board):
    rows, cols = len(board), len(board[0])
    out = []
    for c in range(cols):
        col = []
        for r in range(rows - 1, -1, -1):
            if board[r][c] == 0:
                break
            col.append(board[r][c])
        out.append(tuple(col))
    return tuple(out)


def _random_position(rng, rows, cols, max_free):
    board, p = empty_board(rows, cols), 1
    for _ in range(rng.randint(max(0, rows * cols - max_free), rows * cols)):
        free = legal_columns(board)
        if not free:
            return None
        mv = apply_move(board, rng.choice(free), p)
        if check_win_at(board, mv, p) or not legal_columns(board):
            return None
        p = 3 - p
    return (board, p) if legal_columns(board) else None


def _check(board, p, rows, cols, order):
    o = _Oracle(rows, cols)
    st = _to_state(board)
    res = solve_position([r[:] for r in board], p, order=order)
    exact = o.exact(st, p)
    exact_p1 = exact if p == 1 else -exact  # Demo kodiert aus Sicht Rot
    assert res.value == exact_p1
    assert o.child(st, res.best_column, p) == exact  # gewählter Zug ist wirklich optimal
    counter = [0]
    o.negamax(st, p, -2, 2, order, counter)
    assert res.node_count == counter[0]


@pytest.mark.parametrize("order", ORDERS)
def test_random_positions_match_oracle(order):
    rng = random.Random(11)
    done = 0
    while done < 40:
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        pos = _random_position(rng, rows, cols, 8)
        if pos is None:
            continue
        _check(pos[0], pos[1], rows, cols, order)
        done += 1


@pytest.mark.parametrize(
    "rows,cols,expected",
    [
        (3, 3, [213, 213, 213, 213]),
        (4, 3, [749, 749, 1286, 601]),
    ],
)
def test_empty_board_counts_match_oracle_for_all_orders(rows, cols, expected):
    o = _Oracle(rows, cols)
    st = tuple(() for _ in range(cols))
    order_list = (ORDER_NAIVE, ORDER_CENTER_FIRST, ORDER_WORST_CASE, ORDER_BEST_CASE)
    for order, exp in zip(order_list, expected):
        counter = [0]
        o.negamax(st, 1, -2, 2, order, counter)
        assert counter[0] == exp
        assert solve_position(empty_board(rows, cols), 1, order=order).node_count == exp
