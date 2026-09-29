"""Regressionstest gegen den in minimax-demo gefundenen scaleanchor+range-Bug
(Brett im echten Browser unsichtbar, AppTest erkennt es nicht) - hier von
Anfang an mit autorange gebaut, Test hält das fest."""

from ab_game import empty_board
from ab_visualization import board_figure, order_comparison_figure


def test_board_figure_uses_autorange_not_explicit_range():
    board = empty_board(4, 3)
    fig = board_figure(board, None, None, 1)
    assert fig.layout.xaxis.autorange is True
    assert fig.layout.xaxis.range is None
    assert fig.layout.yaxis.autorange is True
    assert fig.layout.yaxis.range is None


def test_board_figure_cell_count_matches_board_size():
    board = empty_board(3, 4)
    fig = board_figure(board, None, None, None)
    cell_trace = fig.data[0]
    assert len(cell_trace.x) == 3 * 4


def test_order_comparison_figure_has_one_bar_per_order():
    counts = {"naiv": 749, "mitte_zuerst": 900}
    fig = order_comparison_figure(counts, highlight="naiv")
    assert len(fig.data[0].x) == 2
