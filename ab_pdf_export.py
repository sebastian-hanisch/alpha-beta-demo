"""PDF-Export der aktuellen Positions-Analyse (fpdf2).

`multi_cell(w=0, ...)` lässt den Cursor per Default am RECHTEN statt am linken
Rand stehen (anders als `cell`) - ohne `new_x=LMARGIN` würde ein zweiter
`multi_cell`-Aufruf direkt danach mit 0 verbleibender Breite rechnen und
abstürzen (echter, bereits einmal gefundener Bug in minimax-demo, siehe
dortige Moduldoku und Test) - hier von Anfang an korrekt.
"""

from __future__ import annotations

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from ab_constants import ORDER_LABELS, PLAYER_NAMES
from ab_evaluation import format_de_number, to_move_verdict, value_verdict

_NEXT_LINE = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(rows: int, cols: int, moves: list[int], order: str, player_to_move: int, value: int, node_count: int, best_column: int) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Alpha-Beta - Analyse der aktuellen Stellung", **_NEXT_LINE)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Brett: {rows} Zeilen x {cols} Spalten", **_NEXT_LINE)
    move_text = ", ".join(str(m) for m in moves) if moves else "keine (Startstellung)"
    pdf.cell(0, 8, f"Bisherige Züge (Spalten): {move_text}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Zugreihenfolge: {ORDER_LABELS[order]}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Am Zug: {PLAYER_NAMES[player_to_move]}", **_NEXT_LINE)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Ergebnis der Alpha-Beta-Suche", **_NEXT_LINE)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, value_verdict(value), **_NEXT_LINE)
    pdf.multi_cell(0, 8, to_move_verdict(value, player_to_move), **_NEXT_LINE)
    pdf.cell(0, 8, f"Durchsuchte Knoten: {format_de_number(node_count)}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Gewählte Spalte: {best_column}", **_NEXT_LINE)

    return bytes(pdf.output())
