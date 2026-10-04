"""Alpha-Beta-Pruning: derselbe Spielwert wie Minimax, aber wie viele Knoten
weniger - abhängig von der Zugreihenfolge.

Kind-Stück von minimax-demo (Wurzel der Adversarische-Suche-Linie).
"""

from __future__ import annotations

import streamlit as st

import ab_constants as C
from ab_alphabeta import NodeCounter, solve_position
from ab_evaluation import format_de_number, to_move_verdict, value_verdict
from ab_game import replay
from ab_pdf_export import build_pdf
from ab_presets import (
    PRESET_HELP,
    PRESETS,
    apply_preset,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from ab_visualization import board_figure, order_comparison_figure

_de = format_de_number

st.set_page_config(page_title="Alpha-Beta – Sebastian Hanisch", layout="wide")

st.title("✂️ Alpha-Beta-Pruning: derselbe Wert, viel weniger Suche")
st.markdown(
    """
    **Alpha-Beta-Pruning** liefert für jede Stellung exakt denselben Spielwert wie die
    volle Minimax-Suche aus dem Elternstück – bewiesen, kein Kompromiss. Der Unterschied
    ist die **Zahl der besuchten Suchknoten**: sobald ein Ast beweisbar nicht mehr besser
    werden kann als eine bereits gefundene Alternative, wird er abgeschnitten, statt ihn
    zu Ende durchzusuchen. Wie stark das hilft, hängt stark von der **Zugreihenfolge** ab
    – das ist der Kern dieser Demo. Am Ende der Seite: die 📐 Mathematische Formulierung.
    """
)

st.caption("🎯 Schnellstart")
preset_cols = st.columns(len(PRESETS))
for col, name in zip(preset_cols, PRESETS):
    col.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])
st.caption("🔗 Die URL merkt sich Brettgröße, Reihenfolge und Zugfolge (Permalink).")

load_permalink_settings()
init_session_state_defaults()


def _boards_allowed_for(order: str) -> list[int]:
    return [i for i, b in enumerate(C.BOARD_OPTIONS) if b["oracle_ok"] or order not in C.ORDERS_NEEDING_ORACLE]


def _on_order_change() -> None:
    allowed = _boards_allowed_for(st.session_state["order_select"])
    if st.session_state["board_index_select"] not in allowed:
        st.session_state["board_index_select"] = C.DEFAULT_BOARD_INDEX
        st.session_state["moves"] = []


def _reset_moves_on_board_change() -> None:
    st.session_state["moves"] = []


with st.sidebar:
    st.header("⚙️ Einstellungen")
    order = st.radio(
        "Zugreihenfolge",
        options=[C.ORDER_NAIVE, C.ORDER_CENTER_FIRST, C.ORDER_WORST_CASE, C.ORDER_BEST_CASE],
        format_func=lambda o: C.ORDER_LABELS[o],
        key="order_select",
        on_change=_on_order_change,
        help="„Bester/schlechtester Fall“ brauchen Vorwissen und sind deshalb nur auf kleinen Brettern verfügbar.",
    )
    allowed_boards = _boards_allowed_for(order)
    if st.session_state["board_index_select"] not in allowed_boards:
        st.session_state["board_index_select"] = C.DEFAULT_BOARD_INDEX
        st.session_state["moves"] = []
    board_index = st.radio(
        "Brettgröße",
        options=allowed_boards,
        format_func=lambda i: C.BOARD_OPTIONS[i]["label"],
        key="board_index_select",
        on_change=_reset_moves_on_board_change,
    )
    if st.button("↺ Neues Spiel", use_container_width=True):
        st.session_state["moves"] = []
        st.rerun()

board_spec = C.BOARD_OPTIONS[board_index]
rows, cols = board_spec["rows"], board_spec["cols"]
moves: list[int] = [m for m in st.session_state["moves"] if 0 <= m < cols]
sync_query_params(board_index, order, moves)


@st.cache_data(show_spinner="Durchsuche mit Alpha-Beta-Pruning ...")
def _replay_and_solve(rows: int, cols: int, moves: tuple[int, ...], order: str):
    state = replay(rows, cols, list(moves))
    if state.is_terminal:
        return state, None
    counter = NodeCounter()
    result = solve_position([row[:] for row in state.board], state.player_to_move, order=order, counter=counter)
    return state, result


@st.cache_data(show_spinner=False)
def _all_order_node_counts(rows: int, cols: int, moves: tuple[int, ...], oracle_ok: bool):
    orders = [C.ORDER_NAIVE, C.ORDER_CENTER_FIRST] + (
        [C.ORDER_WORST_CASE, C.ORDER_BEST_CASE] if oracle_ok else []
    )
    counts = {}
    for o in orders:
        state = replay(rows, cols, list(moves))
        if state.is_terminal:
            continue
        result = solve_position([row[:] for row in state.board], state.player_to_move, order=o)
        counts[o] = result.node_count
    return counts


state, result = _replay_and_solve(rows, cols, tuple(moves), order)

st.subheader("Stellung")
board_col, info_col = st.columns([2, 1])

with board_col:
    best_col = result.best_column if result is not None else None
    fig = board_figure(state.board, state.last_move, state.winner, best_col)
    st.plotly_chart(fig, use_container_width=True, key="board_chart")

    if not state.is_terminal:
        click_cols = st.columns(cols)
        for c, click_col in enumerate(click_cols):
            full_column = state.board[0][c] != C.EMPTY
            label = f"⬇ {c}" + (" ★" if c == best_col else "")
            if click_col.button(label, key=f"drop_{c}", disabled=full_column, use_container_width=True):
                st.session_state["moves"] = moves + [c]
                st.rerun()

with info_col:
    if state.is_terminal:
        if state.winner is not None:
            st.success(f"Spiel beendet: {C.PLAYER_NAMES[state.winner]} hat gewonnen.")
        else:
            st.info("Spiel beendet: Remis (Brett voll).")
    else:
        st.metric("Am Zug", C.PLAYER_NAMES[state.player_to_move])
        st.metric("Durchsuchte Knoten", _de(result.node_count))
        if result.oracle_node_count:
            st.caption(f"+ {_de(result.oracle_node_count)} Knoten Vorwissen-Kosten (nicht mitgezählt).")
        verdict = to_move_verdict(result.value, state.player_to_move)
        if "erzwingen" in verdict and "nicht mehr" not in verdict:
            st.success(verdict)
        elif "verliert" in verdict:
            st.warning(verdict)
        else:
            st.info(verdict)
        st.caption("★ = gefundene optimale Spalte (garantiert exakt, siehe 📐 unten).")

        pdf_bytes = build_pdf(rows, cols, moves, order, state.player_to_move, result.value, result.node_count, best_col)
        st.download_button("📄 Analyse als PDF", data=pdf_bytes, file_name="alphabeta_analyse.pdf", mime="application/pdf")

st.markdown("---")
st.subheader("🔬 Wie stark hilft Pruning überhaupt?")
baseline = C.MINIMAX_BASELINE_NODES.get((rows, cols))
if baseline is not None and not state.is_terminal:
    naive_counts = _all_order_node_counts(rows, cols, tuple(moves), board_spec["oracle_ok"])
    naive_ab = naive_counts.get(C.ORDER_NAIVE, result.node_count)
    factor = baseline / naive_ab if naive_ab else float("inf")
    st.success(
        f"Volle Minimax-Suche (minimax-demo, gleiche Startstellung) braucht **{_de(baseline)}** Knoten, "
        f"Alpha-Beta mit naiver Reihenfolge nur **{_de(naive_ab)}** – das **{_de(factor)}**-fache weniger, "
        f"OHNE jedes Vorwissen über gute Züge."
    )
else:
    st.info(
        "Für diese Brettgröße gibt es keinen minimax-demo-Vergleichswert (dort nicht gemessen, da "
        "die volle Suche hier bereits unbrauchbar langsam wäre)."
    )

st.subheader("🔬 Wie stark hängt der Erfolg von der Zugreihenfolge ab?")
if not state.is_terminal:
    counts = _all_order_node_counts(rows, cols, tuple(moves), board_spec["oracle_ok"])
    st.plotly_chart(order_comparison_figure(counts, highlight=order), use_container_width=True, key="order_chart")
    if board_spec["oracle_ok"]:
        worst = counts[C.ORDER_WORST_CASE]
        best = counts[C.ORDER_BEST_CASE]
        if best > 0:
            st.success(
                f"Schlechtester Fall: **{_de(worst)}** Knoten. Bester Fall: **{_de(best)}** Knoten – "
                f"ein Faktor **{_de(worst / best, 1)}** allein durch die Reihenfolge, bei identischem Ergebnis."
            )
        else:
            st.info("Bester Fall braucht auf dieser Stellung praktisch keine Suche mehr.")
    else:
        st.info(
            "„Bester/schlechtester Fall“ sind auf dieser Brettgröße nicht verfügbar – das Vorwissen dafür "
            "(eine vollständige Lösung der ganzen Stellung als Orakel) wäre hier selbst schon zu teuer "
            "(auf 4×4 allein 334s, siehe minimax-demo)."
        )
else:
    st.info("Spiel bereits beendet - kein weiterer Suchbaum zu vergleichen.")

st.markdown("---")
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
    - **„Bester/schlechtester Fall“ sind kein echter Algorithmus.** Sie brauchen ein Orakel (eine
      vollständige Lösung der Stellung im Voraus) und sind deshalb nur auf kleinen Brettern gezeigt –
      in der Praxis kennt kein Programm die Werte im Voraus.
    - **„Mitte zuerst“ hilft nicht immer.** Auf 4×4 braucht diese echte, oft genutzte Heuristik hier
      MEHR Knoten als die naive Reihenfolge (108.671 vs. 43.827, siehe README) – eine plausible
      Heuristik ist kein Erfolgsgarant, das muss gemessen werden.
    - **Nur EIN optimaler Zug ist garantiert exakt.** Anders als in minimax-demo (volle Suche kennt ALLE
      gleichwertigen Züge) liefert ein einzelner Alpha-Beta-Lauf mit vollem Fenster nur für den
      tatsächlich gewählten besten Zug einen beweisbar exakten Wert – für schlechtere Züge oft nur eine
      Schranke, kein exakter Wert (echter, bewusster Umfangsverzicht dieses Stücks).
    """
)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
        Wie Minimax, zusätzlich mit einem Fenster $[\alpha, \beta]$, das während der Suche enger wird:

        $$
        \alpha\text{-}\beta(s, \alpha, \beta) =
        \begin{cases}
        \text{Endwert} & s \text{ ist Sieg/Remis} \\
        v & \text{sobald } \alpha \geq \beta \text{ (Abschneiden)}
        \end{cases}
        $$

        Für Rot (maximierend) wird $\alpha$ nach jedem Zug auf den bisher besten Wert angehoben; sobald
        $\alpha \geq \beta$, kann kein weiterer Zug dieses Knotens das Ergebnis noch verbessern – der Rest
        wird übersprungen, ohne dass ein einziger Knoten davon besucht wird. Für Gelb (minimierend)
        symmetrisch mit $\beta$. Der zurückgegebene Wert ist immer exakt gleich dem von Minimax; nur die
        Zahl der dafür besuchten Knoten unterscheidet sich - siehe die Experimente oben.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Adversarische Suche: Minimax bis Selbstspiel](https://sebastianhanisch.net/konzepte-adversarische-suche.html)."
)
