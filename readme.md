# Fitness-Data-Analyzer

Ein Python-basiertes Analyse- und Visualisierungstool für sportliche Leistungen. Das Tool dient der Auswertung generierter Trainingsdaten und zeigt exemplarisch explorative Datenanalyse (EDA), statistische Bereinigung von Ausreißern und die Erkennung langfristiger Leistungstrends.

## Key Features

* **Zufällige Testdaten-Generierung:** Simulation von Trainingsfortschritten mittels kombinierter linearer und zyklischer Algorithmen inklusive bewusst erstellte Extremwerte.
* **Explorative Anomalie-Erkennung:** Visuelle Identifikation von Ausreißern mittels Boxplots.
* **Statistische Datenbereinigung:** Automatisiertes Aussortieren von Ausreißern über die zweifache Standardabweichung ($\mu \pm 2\sigma$).
* **Geglättete Trendanalyse:** Berechnung und Darstellung der Leistungsprogression mit Hilfe von Rolling Averages.
* **Zusammenhangsanalyse (Feature-Korrelation):** Untersuchung von Wechselwirkungen zwischen Leistungsmetriken (z. B. Trainingsdauer vs. Score-Wertung) mittels Heatmaps.
* **[In Planung] Web-Schnittstelle (REST-API):** Empfang von realen Daten der CLI-App zur automatisierten Verarbeitung innerhalb der Analyse-Pipeline.

## Tech Stack

* **Sprache:** Python 3.x
* **Datenverarbeitung:** `pandas`
* **Visualisierung:** `matplotlib`, `seaborn`
* **Datenbank:** SQLite3
* **Testing:** `pytest`, `unittest`
* **[In Planung] Zusätzliche Bibliotheken:** `FastAPI` (Schnittstellen-Framework) und `Pydantic` (Datenvalidierung)

---

## Schnellstart

Um das Analyse-Tool auszuführen und die Visualisierungen zu betrachten, gehen Sie wie folgt vor:

1. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Datenbasis generieren:**
   ```bash
   python scripts/generate_mock_data.py
   ```
   *Erstellt die SQLite-Datenbank `data/fitness_mock.db` mit 100 realistischen, synthetischen Trainingseinheiten.*
3. **Analyse-Notebook starten:**
   ```bash
   jupyter notebook notebooks/analysis.ipynb
   ```
   *Führt Schritt für Schritt durch die explorative Datenanalyse, Bereinigung und Visualisierung.*

---

## Projektstruktur

* `data/`: Verzeichnis für die SQLite-Datenbank (`fitness_mock.db`).
* `docs/`: Technische Dokumentation der Analyse-Struktur (PlantUML-Quellen und Diagramme).
* `notebooks/`: Jupyter Notebook (`analysis.ipynb`) mit der vollständigen ETL- und Visualisierungs-Pipeline.
* `scripts/`: Ausführbare Python-Skripte zur Datenbereitstellung und -generierung.
  * `generate_mock_data.py`: Logik zur Erzeugung mathematisch modellierter Trainingsdaten.
  * `data_provider.py`: Schnittstelle für zukünftige API-Datenzugriffe.
* `tests/`: Testsuite zur Überprüfung der Datenintegrität und der Testdatengenerierung.
* `requirements.txt`: Liste der benötigten wissenschaftlichen Bibliotheken für die Datenanalyse.

---

## Design-Entscheidungen (Highlights)

### Mathematische Trend-Simulation
Fortschritte im Krafttraining werden über ein mathematisches Modell simuliert, das einen linearen Grundtrend mit einer periodischen Sinuskurve kreuzt. Dadurch werden natürliche Plateaus und plötzliche Leistungsschübe realitätsnah abgebildet, während ein normalverteiltes Rauschen die Tagesform simuliert.

### Datenbereinigung und Filter-Logik
Das Tool demonstriert zwei unterschiedliche Ansätze im Umgang mit Anomalien:
1. **Statistische Bereinigung (Progression):** Bei der detaillierten Betrachtung der Kniebeugen werden fehlerhafte Datensätze (0-kg-Einträge) über das mathematische Kriterium der zweifachen Standardabweichung ($\mu \pm 2\sigma$) automatisiert isoliert und eliminiert, um den gleitenden Durchschnitt nicht zu verzerren.
2. **Heuristische Filterung (Zusammenhangsanalyse):** Vor der Erstellung der Heatmap werden über feste Schwellenwerte unvollständige Trainingseinheiten (Wertung = 0) sowie extreme Zeit-Ausreißer manuell begrenzt, um die Korrelationsmatrix auf die primären Leistungskorridore zu fokussieren.

---

## Architektur & Dokumentation

Das Tool ist als eigenständige Pipeline konzipiert, die synthetische Trainingsdaten generiert, diese über relationale Strukturen persistiert und anschließend für statistische Auswertungen transformiert. Die aktuellen Abläufe sind in den folgenden Diagrammen dokumentiert:

### Interner Daten-Generierungsprozess (Sequenzdiagramm)
Das Sequenzdiagramm zeigt den Ablauf des Skripts `generate_mock_data.py`. Es stellt die Berechnung zur Simulation einer natürlichlich Progression dar, welche auch gezielt ausreißer einbaut. Ebenso dass es die relationalen SQL-Tabellen unter Einhaltung der Fremdschlüssel-Hierarchien befüllt.

![Sequenzdiagramm Datengenerierung](./docs/generate_mock_data.svg)

### Lokale Analyse-Pipeline (Aktivitätsdiagramm)
Dieses Diagramm visualisiert den sequenziellen ETL-Prozess (Extract, Transform, Load) innerhalb des Jupyter Notebooks (`analysis.ipynb`). Es zeigt den Weg der Rohdaten aus der lokalen SQLite-Datenbank, Ermittlung von Ausreißern, Darstellung statistischen Korrelation und Visualisierung.

![Aktivitätsdiagramm Daten-Pipeline](./docs/pipeline.svg)

### Konzeptionelle Gesamtarchitektur (Zielbild)
Die langfristige Systemarchitektur sieht eine datentechnische Brücke zwischen dem **Fitness-Tracker CLI** und diesem **Fitness-Data-Analyzer** vor. In diesem Zielbild werden die lokalen Datei-Zugriffe auf die `.db`-Dateien durch den geplanten FastAPI-Layer ersetzt. Der Analyzer fungiert dann als zentrale Datensenke-Dienst, der Workouts über standardisierte Web-Schnittstellen empfängt und plattformunabhängig auswertet.

![Gesamtarchitektur Zielbild](./docs/architecture_target.svg)

---

## Testing

Die Testsuite im Ordner `tests/` stellt die Validität der Datenbasis und Berechnungslogiken sicher:

* `test_generator.py`: Überprüfung der Tabellenerstellung, der Progressionsbrechnungen und Stabilität der Datengenerierung.
* `test_db_connection.py`: Integrationstest zur Verifizierung erfolgreicher Lese- und Schreibzugriffe auf die SQLite-Schnittstelle.
* `test_data_integrity.py`: Prüft die Korrektheit von mathematischen Zusammenhängen innerhalb der generierten Tabellen.

**Tests ausführen:**
```bash
python -m pytest tests/ -v
```

---

## Ausblick und API-Konzept (Future Work)

Um das Analyse-Tool nicht nur auf zufällig generierte Testdaten sowie manuell eingefügte Datenbank-Dateien anwenden zu können, ist die Implementierung einer Webschnittstelle (REST-API) auf Basis von FastAPI geplant.

### Geplante Architektur-Erweiterung

1. **API-Schnittstelle:** Das Analyse-Tool stellt Endpunkte bereit, um Trainingsdaten direkt aus externen Quellen (wie der CLI-App) entgegenzunehmen, anstatt direkt auf deren lokale Datenbank zuzugreifen.
2. **Entkoppelte Pipeline:** Eingehende Daten werden direkt im Speicher über Pydantic-Modelle validiert und fließen direkt in die bestehende Pandas- und Seaborn-Pipeline ein.
3. **Zentraler Datenspeicher:** Die `fitness_mock.db` wird langfristig durch eine produktive Datenbanklösung ersetzt, welche sowohl transaktionale Schreibzugriffe der App als auch analytische Lesezugriffe des Tools via API bedienen kann.

---

## Lizenz

Dieses Projekt wurde zu Bildungszwecken im Rahmen eines Portfolios erstellt.
Frei zur Nutzung und Modifikation.
```