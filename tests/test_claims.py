"""Jede Zahl aus dem README wird hier gegen den tatsächlichen Code nachgerechnet."""

import pytest

from ab_constants import ORDER_BEST_CASE, ORDER_CENTER_FIRST, ORDER_NAIVE, ORDER_WORST_CASE, PLAYER_ONE
from ab_game import empty_board
from ab_alphabeta import solve_position


@pytest.mark.parametrize(
    "rows,cols,order,expected_nodes",
    [
        (3, 3, ORDER_NAIVE, 213),
        (4, 3, ORDER_NAIVE, 749),
        (3, 4, ORDER_NAIVE, 2_826),
        (4, 4, ORDER_NAIVE, 43_827),
        (4, 4, ORDER_CENTER_FIRST, 108_671),
        (4, 3, ORDER_WORST_CASE, 1_286),
        (4, 3, ORDER_BEST_CASE, 601),
    ],
)
def test_readme_node_counts(rows, cols, order, expected_nodes):
    board = empty_board(rows, cols)
    result = solve_position(board, PLAYER_ONE, order=order)
    assert result.node_count == expected_nodes


def test_readme_all_boards_are_draws():
    for rows, cols in [(3, 3), (4, 3), (3, 4), (4, 4)]:
        board = empty_board(rows, cols)
        result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE)
        assert result.value == 0


def test_readme_4x4_reduction_factor_vs_minimax_demo():
    from ab_constants import MINIMAX_BASELINE_NODES

    board = empty_board(4, 4)
    naive = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE).node_count
    factor = MINIMAX_BASELINE_NODES[(4, 4)] / naive
    assert factor == pytest.approx(1895, abs=1)


def test_readme_4x3_worst_vs_best_factor():
    worst = solve_position(empty_board(4, 3), PLAYER_ONE, order=ORDER_WORST_CASE).node_count
    best = solve_position(empty_board(4, 3), PLAYER_ONE, order=ORDER_BEST_CASE).node_count
    assert worst / best == pytest.approx(2.1, abs=0.05)
