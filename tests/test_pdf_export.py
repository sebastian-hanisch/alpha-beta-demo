"""Regressionstest: aufeinanderfolgende multi_cell-Aufrufe dürfen nicht crashen
(siehe minimax-demo - hier von Anfang an mit new_x=LMARGIN gebaut)."""

from ab_constants import ORDER_NAIVE, PLAYER_ONE
from ab_game import empty_board
from ab_alphabeta import solve_position
from ab_pdf_export import build_pdf


def test_build_pdf_does_not_crash():
    board = empty_board(4, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE)
    pdf_bytes = build_pdf(4, 3, [], ORDER_NAIVE, PLAYER_ONE, result.value, result.node_count, result.best_column)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500
