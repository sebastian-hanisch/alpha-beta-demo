"""Kennzahlen und Verdikt-Texte rund um eine gelöste Position."""

from __future__ import annotations

from ab_constants import PLAYER_NAMES, PLAYER_ONE, PLAYER_TWO


def value_verdict(value: int) -> str:
    if value == 0:
        return "Bei perfektem Spiel beider Seiten endet diese Position remis."
    winner = PLAYER_ONE if value > 0 else PLAYER_TWO
    return f"Bei perfektem Spiel beider Seiten gewinnt {PLAYER_NAMES[winner]}."


def to_move_verdict(value: int, player_to_move: int) -> str:
    outcome_for_mover = value if player_to_move == PLAYER_ONE else -value
    name = PLAYER_NAMES[player_to_move]
    if outcome_for_mover == 0:
        return f"{name} kann das Remis erzwingen, aber nicht mehr gewinnen."
    if outcome_for_mover > 0:
        return f"{name} kann den Sieg erzwingen."
    return f"{name} verliert bei perfektem Gegenspiel - jeder Zug ist gleich schlecht."


def format_de_number(value: float, decimals: int = 0) -> str:
    """Deutsches Tausendertrennzeichen NUR für diese Zahl (siehe minimax-demo:
    ein blankes `.replace(",", ".")` auf einem ganzen Satz zerstört echte
    Satzkommas daneben)."""
    return f"{value:,.{decimals}f}".replace(",", ".")
