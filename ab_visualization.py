"""Plotly-Figuren: Brett-Darstellung und Reihenfolge-Vergleich (alle Achsen fest).

Board-Figur direkt mit `autorange` statt expliziter `range` (siehe minimax-demo:
`scaleanchor` + explizite `range` friert den Bereich beim ersten Zeichnen
anhand der Containerbreite ein - Brett wird unsichtbar).
"""

from __future__ import annotations

import plotly.graph_objects as go

from ab_constants import EMPTY, EMPTY_COLOUR, ORDER_LABELS, PLAYER_COLOURS
from ab_game import winning_line


def board_figure(board, last_move, winner: int | None, best_column: int | None = None) -> go.Figure:
    rows, cols = len(board), len(board[0])
    fig = go.Figure()

    win_cells = set()
    if winner is not None and last_move is not None:
        line = winning_line(board, last_move, winner)
        if line:
            win_cells = set(line)

    xs, ys, colours, line_widths, line_colours = [], [], [], [], []
    for r in range(rows):
        for c in range(cols):
            value = board[r][c]
            xs.append(c)
            ys.append(rows - 1 - r)
            colours.append(EMPTY_COLOUR if value == EMPTY else PLAYER_COLOURS[value])
            if (r, c) in win_cells:
                line_widths.append(4)
                line_colours.append("#1a1a1a")
            else:
                line_widths.append(1)
                line_colours.append("#9a9a9a")

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker=dict(size=46, color=colours, line=dict(width=line_widths, color=line_colours)),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    if best_column is not None:
        fig.add_trace(
            go.Scatter(
                x=[best_column],
                y=[rows + 0.35],
                mode="markers",
                marker=dict(size=16, color="#2ca02c", symbol="triangle-down"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Unsichtbare Eckmarker statt expliziter range (siehe Moduldoku).
    fig.add_trace(
        go.Scatter(
            x=[-0.7, cols - 0.3],
            y=[-0.7, rows + 0.9],
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_xaxes(autorange=True, showgrid=False, zeroline=False, showticklabels=False, fixedrange=True)
    fig.update_yaxes(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        fixedrange=True,
        scaleanchor="x",
        scaleratio=1,
    )
    fig.update_layout(height=110 * rows + 140, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="#f7f7f7")
    return fig


def order_comparison_figure(node_counts: dict[str, int], highlight: str | None = None) -> go.Figure:
    orders = list(node_counts.keys())
    labels = [ORDER_LABELS[o].split(" (")[0] for o in orders]
    nodes = [node_counts[o] for o in orders]
    colours = ["#2ca02c" if o == highlight else "#1f77b4" for o in orders]
    texts = [f"{n:,}".replace(",", ".") for n in nodes]

    fig = go.Figure(go.Bar(x=labels, y=nodes, marker_color=colours, text=texts, textposition="outside"))
    fig.update_yaxes(title="Suchknoten", fixedrange=True)
    fig.update_xaxes(title="Zugreihenfolge", fixedrange=True)
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
    return fig
