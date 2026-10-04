"""PRESETS, Permalink (Begrenzen/Einrasten), Session-Defaults."""

from __future__ import annotations

import streamlit as st

from ab_constants import BOARD_OPTIONS, DEFAULT_BOARD_INDEX, ORDER_CENTER_FIRST, ORDER_NAIVE

PRESETS = {
    "Naiv (4×3)": {"board_index": 1, "order": ORDER_NAIVE, "moves": []},
    "Mitte zuerst (4×3)": {"board_index": 1, "order": ORDER_CENTER_FIRST, "moves": []},
    "Naiv auf 4×4": {"board_index": 3, "order": ORDER_NAIVE, "moves": []},
}
PRESET_HELP = {
    "Naiv (4×3)": "Standardgröße dieser Linie (wie minimax-demo), ohne Heuristik.",
    "Mitte zuerst (4×3)": "Dieselbe Größe, echte Heuristik statt naiver Reihenfolge.",
    "Naiv auf 4×4": "Das Brett, das in minimax-demo noch 334s brauchte - hier in Sekundenbruchteilen.",
}

_DEFAULTS = {"board_index": DEFAULT_BOARD_INDEX, "order": ORDER_NAIVE, "moves": []}


def apply_preset(name: str) -> None:
    preset = PRESETS[name]
    st.session_state["board_index_select"] = preset["board_index"]
    st.session_state["order_select"] = preset["order"]
    st.session_state["moves"] = list(preset["moves"])


def init_session_state_defaults() -> None:
    if "board_index_select" not in st.session_state:
        st.session_state["board_index_select"] = _DEFAULTS["board_index"]
    if "order_select" not in st.session_state:
        st.session_state["order_select"] = _DEFAULTS["order"]
    if "moves" not in st.session_state:
        st.session_state["moves"] = list(_DEFAULTS["moves"])


def _parse_moves(raw: str) -> list[int]:
    if not raw:
        return []
    try:
        return [int(x) for x in raw.split(",") if x != ""]
    except ValueError:
        return []


def load_permalink_settings() -> None:
    """Lädt Brettgröße/Reihenfolge/Zugfolge aus der URL - NUR beim allerersten
    Lauf dieser Session (sonst würde jeder Klick sofort wieder rückgängig
    gemacht - echter, bereits einmal gefundener Bug in minimax-demo, siehe
    dortige Moduldoku)."""
    if "board_index_select" in st.session_state:
        return
    params = st.query_params
    if "board" not in params and "moves" not in params and "order" not in params:
        return

    board_index = _DEFAULTS["board_index"]
    if "board" in params:
        try:
            candidate = int(params["board"])
        except ValueError:
            candidate = board_index
        if 0 <= candidate < len(BOARD_OPTIONS):
            board_index = candidate

    order = params.get("order", _DEFAULTS["order"])
    if order not in {ORDER_NAIVE, ORDER_CENTER_FIRST, "schlechtester_fall", "bester_fall"}:
        order = _DEFAULTS["order"]

    moves = _parse_moves(params.get("moves", ""))
    st.session_state["board_index_select"] = board_index
    st.session_state["order_select"] = order
    st.session_state["moves"] = moves


def sync_query_params(board_index: int, order: str, moves: list[int]) -> None:
    st.query_params["board"] = str(board_index)
    st.query_params["order"] = order
    st.query_params["moves"] = ",".join(str(m) for m in moves)
