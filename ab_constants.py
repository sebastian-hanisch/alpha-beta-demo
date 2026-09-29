"""Regler-Grenzen, feste Annahmen, Farben."""

WIN_LENGTH = 4
EMPTY = 0
PLAYER_ONE = 1  # beginnt immer, entspricht "Rot"
PLAYER_TWO = 2  # "Gelb"

PLAYER_NAMES = {PLAYER_ONE: "Rot", PLAYER_TWO: "Gelb"}
PLAYER_COLOURS = {PLAYER_ONE: "#d62728", PLAYER_TWO: "#f2c744"}
EMPTY_COLOUR = "#e5e5e5"

ORDER_NAIVE = "naiv"
ORDER_CENTER_FIRST = "mitte_zuerst"
ORDER_WORST_CASE = "schlechtester_fall"
ORDER_BEST_CASE = "bester_fall"

ORDER_LABELS = {
    ORDER_NAIVE: "Naiv (Spalte 0, 1, 2, ... der Reihe nach)",
    ORDER_CENTER_FIRST: "Mitte zuerst (echte Heuristik, kein Vorwissen)",
    ORDER_WORST_CASE: "Schlechtester Fall (bewusst falsch herum, braucht Vorwissen)",
    ORDER_BEST_CASE: "Bester Fall (Orakel-Reihenfolge, braucht Vorwissen)",
}
ORDER_HELP = {
    ORDER_NAIVE: "Spalten werden immer von links nach rechts probiert - der Standard ohne jede Heuristik.",
    ORDER_CENTER_FIRST: (
        "Mittlere Spalten zuerst - eine echte, oft genutzte Vier-Gewinnt-Heuristik (keine Vorausberechnung "
        "nötig)."
    ),
    ORDER_WORST_CASE: (
        "Spalten werden absichtlich von der schlechtesten zur besten sortiert (Orakel-Wissen nötig) - zeigt "
        "die Untergrenze des Nutzens von Alpha-Beta."
    ),
    ORDER_BEST_CASE: (
        "Spalten werden von der besten zur schlechtesten sortiert (Orakel-Wissen nötig) - zeigt die "
        "theoretische Obergrenze des Pruning-Effekts."
    ),
}

ORDERS_NEEDING_ORACLE = frozenset({ORDER_WORST_CASE, ORDER_BEST_CASE})

# Live wählbare Brettgrößen - vorab gemessen (tools/PRESET_SWEEP.md). "naiv" und
# "mitte_zuerst" brauchen kein Vorwissen und laufen auf allen sechs Formen unter
# ~3s; "bester_fall"/"schlechtester_fall" brauchen zusätzlich eine EINMALIGE
# vollständige Lösung der Stellung als Orakel (siehe ab_alphabeta.py) - deren
# Kosten sind nur für die drei Formen aus minimax-demo bereits bekannt und
# günstig (<=700.777 Knoten, <2,4s); für die drei größeren Formen (4x4, 5x4,
# 3x5) wäre das Orakel selbst schon zu teuer (4x4 allein: 334s, gemessen in
# minimax-demo) - deshalb dort NICHT angeboten.
BOARD_OPTIONS = [
    {"rows": 3, "cols": 3, "label": "3 × 3", "oracle_ok": True},
    {"rows": 4, "cols": 3, "label": "4 Zeilen × 3 Spalten", "oracle_ok": True},
    {"rows": 3, "cols": 4, "label": "3 Zeilen × 4 Spalten", "oracle_ok": True},
    {"rows": 4, "cols": 4, "label": "4 × 4", "oracle_ok": False},
    {"rows": 5, "cols": 4, "label": "5 Zeilen × 4 Spalten", "oracle_ok": False},
    {"rows": 3, "cols": 5, "label": "3 Zeilen × 5 Spalten", "oracle_ok": False},
]
DEFAULT_BOARD_INDEX = 1  # 4x3 - identisch zum Standard in minimax-demo

# Vorab gemessene Referenzpunkte, NICHT live wählbar (zu langsam selbst mit
# Pruning bei naiver Reihenfolge).
MEASURED_TOO_SLOW = [
    {"rows": 4, "cols": 5, "nodes": 12_480_661, "seconds": 43.39, "order": ORDER_NAIVE},
]

# Aus minimax-demo (dieselbe Suche ohne jedes Pruning, ab dem leeren Brett) -
# Referenz für den "wie viel bringt Pruning überhaupt"-Vergleich.
MINIMAX_BASELINE_NODES = {
    (3, 3): 3_568,
    (4, 3): 69_877,
    (3, 4): 700_777,
    (4, 4): 83_078_201,
}
