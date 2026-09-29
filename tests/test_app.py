"""Rauchtests der Streamlit-Oberfläche per AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import ab_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=60)
    if setup is not None:
        setup(at)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Stellung" in h.value for h in at.subheader)


def test_every_naive_board_option_renders():
    for index in range(len(C.BOARD_OPTIONS)):

        def setup(at, index=index):
            at.session_state["order_select"] = C.ORDER_NAIVE
            at.session_state["board_index_select"] = index
            at.session_state["moves"] = []

        _run(setup)


def test_oracle_orders_render_on_small_boards():
    for order in (C.ORDER_WORST_CASE, C.ORDER_BEST_CASE):

        def setup(at, order=order):
            at.session_state["order_select"] = order
            at.session_state["board_index_select"] = 1  # 4x3, oracle_ok
            at.session_state["moves"] = []

        _run(setup)


def test_switching_to_oracle_order_clamps_a_large_board_back_down():
    # 4x4 (index 3) hat oracle_ok=False - beim Wechsel zu bester_fall MUSS die
    # App auf ein oracle-faehiges Brett zurueckfallen, sonst wuerde ein
    # unbezahlbares Orakel gestartet.
    def setup(at):
        at.session_state["order_select"] = C.ORDER_NAIVE
        at.session_state["board_index_select"] = 3
        at.session_state["moves"] = []

    at = _run(setup)
    at.radio(key="order_select").set_value(C.ORDER_BEST_CASE)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert C.BOARD_OPTIONS[at.session_state["board_index_select"]]["oracle_ok"] is True


def test_clicking_a_column_button_plays_a_move():
    at = _run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    assert drop_buttons
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.session_state["moves"]) == 1


def test_switching_board_size_resets_moves():
    def setup(at):
        at.session_state["order_select"] = C.ORDER_NAIVE
        at.session_state["board_index_select"] = 1
        at.session_state["moves"] = [0]

    at = _run(setup)
    at.radio(key="board_index_select").set_value(3)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == []


def test_permalink_restores_board_order_and_moves():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["board"] = "1"
    at.query_params["order"] = C.ORDER_CENTER_FIRST
    at.query_params["moves"] = "0,1"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["board_index_select"] == 1
    assert at.session_state["order_select"] == C.ORDER_CENTER_FIRST
    assert at.session_state["moves"] == [0, 1]


def test_permalink_does_not_get_clobbered_by_later_rerun():
    # Regressionstest fuer den in minimax-demo gefundenen Bug: ohne Session-
    # Guard wuerde load_permalink_settings() bei JEDEM Rerun die Zugfolge aus
    # der (noch nicht aktualisierten) URL ueberschreiben.
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["board"] = "1"
    at.run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == [0]
