"""Korrektheit (Kreuzprobe gegen die in minimax-demo veröffentlichten,
gemessenen Werte) + der Reihenfolge-Effekt, der den Kern dieses Stücks bildet.
"""

import pytest

from ab_constants import ORDER_BEST_CASE, ORDER_CENTER_FIRST, ORDER_NAIVE, ORDER_WORST_CASE, PLAYER_ONE, PLAYER_TWO
from ab_game import apply_move, empty_board
from ab_alphabeta import NodeCounter, solve_position


def test_1x1_board_is_a_trivial_draw():
    board = empty_board(1, 1)
    result = solve_position(board, PLAYER_ONE)
    assert result.value == 0
    assert result.best_column == 0


def test_one_move_from_a_forced_win_is_detected():
    board = empty_board(4, 2)
    for col, player in [(0, PLAYER_ONE), (1, PLAYER_TWO)] * 3:
        apply_move(board, col, player)
    result = solve_position(board, PLAYER_ONE)
    assert result.value == 1
    assert result.best_column == 0


@pytest.mark.parametrize(
    "rows,cols,expected_value",
    [(3, 3, 0), (4, 3, 0), (3, 4, 0), (4, 4, 0)],
)
def test_value_matches_minimax_demo(rows, cols, expected_value):
    # Kreuzprobe: dieselben Spielwerte wie in minimax-demo (dort per voller,
    # ungeprunter Suche gemessen) - Alpha-Beta darf den Wert NIE verändern.
    board = empty_board(rows, cols)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE)
    assert result.value == expected_value


def test_all_four_orderings_agree_on_the_value():
    for order in (ORDER_NAIVE, ORDER_CENTER_FIRST, ORDER_WORST_CASE, ORDER_BEST_CASE):
        board = empty_board(4, 3)
        result = solve_position(board, PLAYER_ONE, order=order)
        assert result.value == 0, order


def test_pruning_reduces_nodes_far_below_naive_minimax_count():
    # minimax-demo misst fuer 4x3 (volle, ungeprunte Suche) 69.877 Knoten.
    board = empty_board(4, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE)
    assert result.node_count < 69_877 / 10


def test_worst_case_ordering_visits_more_nodes_than_best_case():
    # Echter, gemessener Kern-Befund dieses Stuecks: schlechteste Reihenfolge
    # braucht MEHR Knoten als beste, beide brauchen Vorwissen (oracle).
    board_worst = empty_board(4, 3)
    worst = solve_position(board_worst, PLAYER_ONE, order=ORDER_WORST_CASE)
    board_best = empty_board(4, 3)
    best = solve_position(board_best, PLAYER_ONE, order=ORDER_BEST_CASE)
    assert worst.node_count > best.node_count
    assert worst.oracle_node_count > 0
    assert best.oracle_node_count > 0


def test_naive_ordering_has_no_oracle_cost():
    board = empty_board(4, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE)
    assert result.oracle_node_count == 0


def test_3x3_root_children_are_all_tied_so_ordering_cannot_help():
    # Echter, ungewoehnlicher Fund beim Bau: auf 3x3 ziehen bei perfektem Spiel
    # ALLE Eroeffnungszuege remis - eine Sortierung kann auf diesem Brett gar
    # keinen Unterschied machen (alle Kandidaten sind gleich gut).
    board = empty_board(3, 3)
    result = solve_position(board, PLAYER_ONE, order=ORDER_NAIVE)
    assert len(set(result.move_values.values())) == 1


def test_node_count_is_deterministic_across_repeated_runs():
    for order in (ORDER_NAIVE, ORDER_CENTER_FIRST):
        counts = set()
        for _ in range(3):
            board = empty_board(4, 3)
            counts.add(solve_position(board, PLAYER_ONE, order=order).node_count)
        assert len(counts) == 1


def test_solve_is_pure_no_board_mutation():
    board = empty_board(4, 3)
    before = [row[:] for row in board]
    solve_position(board, PLAYER_ONE, order=ORDER_BEST_CASE)
    assert board == before


def test_node_counter_can_be_shared_across_calls():
    counter = NodeCounter()
    board = empty_board(3, 3)
    solve_position(board, PLAYER_ONE, order=ORDER_NAIVE, counter=counter)
    first = counter.count
    board2 = empty_board(3, 3)
    solve_position(board2, PLAYER_ONE, order=ORDER_NAIVE, counter=counter)
    assert counter.count > first
