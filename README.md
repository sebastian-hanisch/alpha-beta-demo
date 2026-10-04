# Alpha-Beta-Pruning: derselbe Wert, viel weniger Suche

**[→ Demo live ausprobieren](https://sebastianhanisch-alpha-beta-demo.streamlit.app/)**

Kind-Stück von **[minimax-demo](https://github.com/sebastian-hanisch/minimax-demo)** (Wurzel der
Adversarische-Suche-Linie). Vehikel: dasselbe Mini-Vier-Gewinnt, dasselbe Brettmodell (`ab_game.py` ist eine
wortgleiche Kopie von `mm_game.py`).

## Warum dieses Problem

Alpha-Beta-Pruning liefert für jede Stellung exakt denselben Spielwert wie volle Minimax-Suche – bewiesen,
kein Kompromiss. Der Unterschied ist die Zahl der besuchten Suchknoten: sobald ein Ast beweisbar nicht mehr
besser werden kann als eine bereits gefundene Alternative, wird er abgeschnitten. Wie stark das hilft, hängt
stark von der **Zugreihenfolge** ab – das ist der Kern dieser Demo.

## Modell

Identisch zu minimax-demo (Board, Zugmechanik, Sieglänge 4). Neu: eine wählbare Zugreihenfolge pro Suche
(`ab_constants.ORDER_*`) und ein Knotenzähler, der die Suchkosten misst, nicht nur das Ergebnis.

## Methodik

Vier Zugreihenfolgen im Vergleich:

- **Naiv**: Spalten der Reihe nach (0, 1, 2, …) – kein Vorwissen.
- **Mitte zuerst**: eine echte, oft genutzte Vier-Gewinnt-Heuristik – kein Vorwissen.
- **Schlechtester/Bester Fall**: brauchen ein **Orakel** – eine einmalige vollständige Lösung der gesamten
  Stellung (dieselbe Suche wie in minimax-demo, dieselben Knotenzahlen), die dann JEDEN Knoten der
  eigentlichen (gemessenen) Suche optimal bzw. pessimal sortiert. Die Orakel-Kosten fließen NICHT in die
  gemessene Knotenzahl ein (wie in der Theorie üblich) und sind deshalb nur auf den drei Brettgrößen aus
  minimax-demo verfügbar, wo sie selbst noch günstig sind (siehe „Ehrliche Grenzen“).

## Befunde (gemessen, keine Behauptungen)

Alle Werte mit der tatsächlich ausgelieferten Suche gemessen (`tests/test_claims.py`), ab dem leeren Brett:

| Brett | naiv | Mitte zuerst | Schlechtester Fall | Bester Fall |
|---|---|---|---|---|
| 3×3 | 213 | 213 | 213 | 213 |
| 4×3 | 749 | 749 | 1.286 | 601 |
| 3×4 | 2.826 | 2.826 | 6.128 | 2.302 |
| 4×4 | 43.827 | 108.671 | – | – |

- **Pruning wirkt gewaltig, schon ohne jedes Vorwissen.** Auf 4×4 braucht die volle Minimax-Suche aus
  minimax-demo 83.078.201 Knoten (334 s) – Alpha-Beta mit naiver Reihenfolge nur 43.827 Knoten (0,15 s):
  das ~1.896-fache weniger. Dadurch werden 4×4, 5×4 und 3×5 hier live wählbar, obwohl sie im Elternstück
  unbrauchbar langsam waren.
- **Auf 3×3 macht die Reihenfolge keinen Unterschied.** Bei perfektem Spiel ziehen dort ALLE
  Eröffnungszüge remis (bereits in minimax-demo gemessen) – jede Sortierung ist auf lauter gleich guten
  Kandidaten wirkungslos. Ein root-only sortierendes Orakel hätte diesen Effekt komplett verpasst (echter
  Fund beim Bau, siehe „Befunde und Korrekturen gegenüber dem Plan“).
- **„Mitte zuerst“ hilft nicht immer.** Auf 4×4 braucht diese echte Heuristik MEHR Knoten als naiv
  (108.671 vs. 43.827) – auf 4×3 nach einem Zug in Spalte 1 dagegen deutlich weniger als naiv. Eine
  plausible Heuristik ist kein Erfolgsgarant, das muss pro Stellung gemessen werden.
- **Schlechtester vs. bester Fall**: auf 4×3 braucht der schlechteste Fall 1.286 Knoten, der beste nur 601
  – Faktor 2,1 allein durch die Reihenfolge, bei identischem Ergebnis.

## Befunde und Korrekturen gegenüber dem Plan

Ursprünglich war geplant, die Bester-/Schlechtester-Fall-Sortierung nur an der WURZEL anzuwenden (billiger
zu berechnen). Erste Messung zeigte: auf 3×3/4×3/3×4 ziehen bei perfektem Spiel ALLE Eröffnungszüge remis
(bereits in minimax-demo gemessen) – eine reine Wurzel-Sortierung wäre auf diesen Brettern komplett
wirkungslos gewesen (stabile Sortierung bei lauter gleichen Werten ändert nichts), hätte den Kern-Hook
dieses Stücks also gerade auf den einzigen Brettern unsichtbar gemacht, auf denen das Orakel überhaupt
bezahlbar ist. Fix: das Orakel liefert den exakten Wert JEDES erreichbaren Zustands (nicht nur der
Wurzelkinder), die Sortierung wird an JEDEM Suchknoten angewendet – dafür wird die einmalige Orakel-Lösung
selbst genutzt (kein zusätzlicher Suchaufwand), ihre Kosten aber separat ausgewiesen, nicht mitgezählt.

## Ehrliche Grenzen

- **„Bester/schlechtester Fall“ sind kein echter Algorithmus**, sondern setzen ein Orakel voraus – nur zur
  Veranschaulichung der theoretischen Grenzen, nicht praktisch nutzbar.
- **Nur EIN optimaler Zug ist garantiert exakt.** Anders als in minimax-demo (kennt alle gleichwertigen
  Züge) liefert ein Alpha-Beta-Lauf mit vollem Fenster nur für den tatsächlich gewählten besten Zug einen
  beweisbar exakten Wert – für schlechtere Züge oft nur eine Schranke.
- Kein öffentlicher Referenzlöser für diese Nicht-Standardgrößen – Korrektheit über Kreuzprobe gegen die
  in minimax-demo gemessenen Spielwerte abgesichert (`tests/test_alphabeta.py`).

## Tests

49 Tests (`pytest tests/ -v`): Brettmechanik, Suchalgorithmus (Kreuzprobe gegen minimax-demo-Werte,
Reihenfolge-Effekt), PDF-Export, Visualisierung, Streamlit-Rauchtests (AppTest: jede Brettgröße/Reihenfolge,
Orakel-Clamp beim Reihenfolgewechsel, Permalink-Rundlauf). Zwei echte Bugs beim Bau gefunden+gefixt: ein
root-only-Orakel wäre auf den einzigen bezahlbaren Brettgrößen wirkungslos gewesen (siehe oben), und der
Ellipsis-Charakter „…“ in einem Radio-Label ließ `fpdf2`s Helvetica-Kernschrift abstürzen (wie der bereits
bekannte Fall mit Gedankenstrich/€, hier zum ersten Mal mit „…“) – behoben mit „...“.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `ab_constants.py` | Brettgrößen, Reihenfolgen, gemessene Referenzwerte |
| `ab_game.py` | Brettmechanik (Kopie von minimax-demo) |
| `ab_alphabeta.py` | Alpha-Beta-Suche + Orakel für Bester/Schlechtester Fall |
| `ab_evaluation.py` | Verdikt-Texte, Zahlenformatierung |
| `ab_visualization.py` | Plotly-Brett und Reihenfolge-Vergleich |
| `ab_presets.py` | Presets, Permalink, Session-Defaults |
| `ab_pdf_export.py` | PDF-Export |

## Bewusst nicht umgesetzt

- Transpositionstabellen (Gegenstand des nächsten Kind-Stücks).
- Move-Ordering-Verfeinerungen wie Killer Moves/History Heuristic (Fußnote im DAG-Scoping, kein eigenes
  Stück).

## Lokal ausführen

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Adversarische Suche: Minimax bis Selbstspiel](https://sebastianhanisch.net/konzepte-adversarische-suche.html).
