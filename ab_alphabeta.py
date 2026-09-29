"""Alpha-Beta-Pruning auf demselben Spielbaum wie `minimax-demo` (Wurzel dieser
Linie), mit wählbarer Zugreihenfolge.

Kernidee: Alpha-Beta liefert IMMER denselben Spielwert wie volle Minimax-Suche
(bewiesen, kein Kompromiss), aber besucht je nach Zugreihenfolge sehr
unterschiedlich viele Knoten.

"Bester/schlechtester Fall" brauchen Vorwissen: eine EINMALIGE vollständige
Lösung der gesamten Stellung (`_oracle_values`, exakt dieselbe erschöpfende
Suche wie in minimax-demo, dieselben Knotenzahlen) liefert den exakten Wert
JEDES erreichbaren Zustands. Diese Vorwissen-Kosten werden bewusst NICHT in
die gemessene `node_count` des eigentlichen (a-priori-sortierten) Laufs
eingerechnet - wie in der Theorie üblich, wo die besten/schlechtesten Schranken
eine gegebene Reihenfolge voraussetzen, nicht deren Berechnung. Echter Fund
beim Bau: auf den kleinsten Brettern (3x3/4x3/3x4) ziehen bei perfektem Spiel
ALLE Eröffnungszüge remis (siehe minimax-demo) - eine Sortierung, die nur an
der WURZEL ansetzt, wäre auf diesen Brettern wirkungslos (alle Wurzelkinder
sind gleich gut, eine stabile Sortierung ändert nichts). Die Orakel-Sortierung
wird deshalb an JEDEM Knoten angewendet, nicht nur an der Wurzel.

"Mitte zuerst" braucht dagegen kein Vorwissen (an jedem Knoten günstig
berechenbar) und wird ebenfalls an jedem Knoten angewendet.
"""

from __future__ import annotations

from dataclasses import dataclass

from ab_constants import ORDER_BEST_CASE, ORDER_CENTER_FIRST, ORDER_NAIVE, ORDER_WORST_CASE, PLAYER_ONE
from ab_game import apply_move, check_win_at, is_full, legal_columns, other_player, undo_move

_NEG_INF, _POS_INF = -2, 2


@dataclass
class NodeCounter:
    count: int = 0


@dataclass
class SolveResult:
    value: int
    node_count: int
    best_column: int
    move_values: dict[int, int]
    oracle_node_count: int = 0  # Vorwissen-Kosten (nur bei bester_fall/schlechtester_fall > 0)


def _center_first_order(cols: list[int], width: int) -> list[int]:
    centre = (width - 1) / 2
    return sorted(cols, key=lambda c: abs(c - centre))


def _terminal_value(board, move, player) -> int | None:
    if check_win_at(board, move, player):
        return 1 if player == PLAYER_ONE else -1
    if is_full(board):
        return 0
    return None


def _board_key(board, player) -> tuple:
    return (tuple(tuple(row) for row in board), player)


def _oracle_values(board, player, counter: NodeCounter) -> dict[tuple, int]:
    """Vollständige, ungeprunte Suche (wortgleiche Struktur zu mm_minimax aus
    minimax-demo) - füllt `cache` mit dem exakten Wert JEDES besuchten
    Zustands, statt nur den Wurzelwert zurückzugeben."""
    cache: dict[tuple, int] = {}

    def rec(b, p) -> int:
        counter.count += 1
        move_values = {}
        for col in legal_columns(b):
            move = apply_move(b, col, p)
            terminal = _terminal_value(b, move, p)
            value = terminal if terminal is not None else rec(b, other_player(p))
            move_values[col] = value
            undo_move(b, move)
        value = max(move_values.values()) if p == PLAYER_ONE else min(move_values.values())
        cache[_board_key(b, p)] = value
        return value

    rec(board, player)
    return cache


def _recurse(board, player, alpha, beta, counter: NodeCounter, order: str, oracle: dict | None) -> int:
    counter.count += 1
    cols = _ordered_columns(board, player, order, oracle)
    best = None
    for col in cols:
        move = apply_move(board, col, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), alpha, beta, counter, order, oracle)
        undo_move(board, move)
        if player == PLAYER_ONE:
            if best is None or value > best:
                best = value
            alpha = max(alpha, best)
        else:
            if best is None or value < best:
                best = value
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def _ordered_columns(board, player, order: str, oracle: dict | None) -> list[int]:
    cols = legal_columns(board)
    if order == ORDER_CENTER_FIRST:
        return _center_first_order(cols, len(board[0]))
    if order in (ORDER_BEST_CASE, ORDER_WORST_CASE):
        maximising = player == PLAYER_ONE
        want_best_first = order == ORDER_BEST_CASE

        def child_value(col: int) -> int:
            move = apply_move(board, col, player)
            terminal = _terminal_value(board, move, player)
            v = terminal if terminal is not None else oracle[_board_key(board, other_player(player))]
            undo_move(board, move)
            return v

        return sorted(cols, key=child_value, reverse=(maximising == want_best_first))
    return cols  # ORDER_NAIVE: natürliche Reihenfolge 0..cols-1


def solve_position(board, player, order: str = ORDER_NAIVE, counter: NodeCounter | None = None) -> SolveResult:
    if counter is None:
        counter = NodeCounter()

    oracle = None
    oracle_node_count = 0
    if order in (ORDER_BEST_CASE, ORDER_WORST_CASE):
        oracle_counter = NodeCounter()
        oracle = _oracle_values(board, player, oracle_counter)
        oracle_node_count = oracle_counter.count

    counter.count += 1
    cols = _ordered_columns(board, player, order, oracle)
    alpha, beta = _NEG_INF, _POS_INF
    best_value = None
    best_col = cols[0] if cols else None
    move_values: dict[int, int] = {}
    for col in cols:
        move = apply_move(board, col, player)
        terminal = _terminal_value(board, move, player)
        value = terminal if terminal is not None else _recurse(board, other_player(player), alpha, beta, counter, order, oracle)
        undo_move(board, move)
        move_values[col] = value
        if player == PLAYER_ONE:
            if best_value is None or value > best_value:
                best_value, best_col = value, col
            alpha = max(alpha, best_value)
        else:
            if best_value is None or value < best_value:
                best_value, best_col = value, col
            beta = min(beta, best_value)
        if alpha >= beta:
            break

    return SolveResult(
        value=best_value,
        node_count=counter.count,
        best_column=best_col,
        move_values=move_values,
        oracle_node_count=oracle_node_count,
    )
