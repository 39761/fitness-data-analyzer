# generate_mock_data.py
# Aufruf mit python scripts/generate_mock_data.py

import sqlite3
import math
import random
import os
from datetime import datetime, timedelta


def create_tables(conn):
    """
    Erstellt die Datenbankstruktur für das Fitness-Analytics-Tool.

    Führt ein SQL-Skript aus, um die Tabellen 'benutzer', 'trainings',
    'dauerlauf_details', 'sprint_details' und 'krafttraining_uebungen'
    anzulegen, falls diese noch nicht existieren.

    Args:
        conn (sqlite3.Connection): Eine bestehende Verbindung zur SQLite-Datenbank.
    """
    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS benutzer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS trainings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nutzer_id INTEGER NOT NULL,
        typ TEXT NOT NULL,
        datum TEXT NOT NULL,
        uhrzeit TEXT NOT NULL,
        dauer_min INTEGER NOT NULL,
        wertung REAL,
        FOREIGN KEY (nutzer_id) REFERENCES benutzer (id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS dauerlauf_details (
        training_id INTEGER PRIMARY KEY,
        distanz_km REAL NOT NULL,
        hf_mittel INTEGER,
        FOREIGN KEY (training_id) REFERENCES trainings (id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS sprint_details (
        training_id INTEGER PRIMARY KEY,
        anzahl INTEGER NOT NULL,
        max_kmh REAL NOT NULL,
        FOREIGN KEY (training_id) REFERENCES trainings (id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS krafttraining_uebungen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        training_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        saetze INTEGER NOT NULL,
        wdh INTEGER NOT NULL,
        gewicht REAL NOT NULL,
        FOREIGN KEY (training_id) REFERENCES trainings (id) ON DELETE CASCADE
    );"""

    cursor.executescript(sql_script)
    conn.commit()  # speichert, falls executescript das nicht automatisch tut


def _calculate_natural_progression(day: int) -> float:
    # linearer Hintergrundfortschritt
    base_trend = day * 0.25

    # Plateau- und Schub-Simulation mittels einer Sinus-Kurve,
    # die eine natürliche Trainingsprogression abbildet
    # Ein voller Zyklus (Plateau + Schub) dauert hier ca. 40 Tage
    wave = math.sin(day / 12.0) * 2.5

    # Stochastisches Rauschen (Tagesform) von +/- 3%
    noise = random.uniform(-0.05, 0.05)

    return base_trend + wave + (base_trend * noise)


def generate_data(db_path="data/fitness_mock.db", num_entries=100):
    """
    Generiert Trainingsdaten für die Fitness-App zu Testzwecken.

    Erstellt eine SQLite-Datenbank mit den Tabellen 'trainings', 'kraft_details',
    'dauerlauf_details' und 'sprint_details'. Simuliert realistische Trends
    und füllt die Tabellen mit zufälligen, aber fachlich plausiblen Werten.

    Args:
        db_path (str): Pfad zur zu erstellenden Datenbankdatei.
        num_entries (int): Anzahl der zu generierenden Basis-Trainingseinheiten.
    """
    # Überprüfen, ob bereits eine aktive Test-Verbindung übergeben wurde
    if isinstance(db_path, sqlite3.Connection):
        conn = db_path
    else:
        # Pfad-Logik und Bereinigung greifen NUR im echten Betrieb (String-Pfad, kein Objekt)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        absolute_db_path = os.path.join(base_dir, "data", "fitness_mock.db")

        os.makedirs(os.path.dirname(absolute_db_path), exist_ok=True)

        # Versuche die Datei komplett zu löschen
        if os.path.exists(absolute_db_path):
            try:
                os.remove(absolute_db_path)
                conn = sqlite3.connect(absolute_db_path)
            except PermissionError:
                # Datei ist blockiert (z.B. durch das Notebook)
                # Wir verbinden uns trotzdem und leeren die Tabellen manuell
                conn = sqlite3.connect(absolute_db_path)
                cursor = conn.cursor()

                # Fremdschlüssel kurz deaktivieren, um Konflikte beim Leeren zu vermeiden
                conn.execute("PRAGMA foreign_keys = OFF;")

                # Tabellen komplett leeren (Inhalte löschen, Struktur bleibt)
                cursor.execute("DELETE FROM krafttraining_uebungen;")
                cursor.execute("DELETE FROM dauerlauf_details;")
                cursor.execute("DELETE FROM sprint_details;")
                cursor.execute("DELETE FROM trainings;")
                cursor.execute("DELETE FROM benutzer;")

                # ID-Zähler (Autoincrement) zurücksetzen
                cursor.execute("DELETE FROM sqlite_sequence;")
                conn.commit()
        else:
            conn = sqlite3.connect(absolute_db_path)

    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )  # SQL wird angewiesen, Fremdschlüssel zu beachten
    create_tables(conn)
    cursor = conn.cursor()

    # Test-Benutzer anlegen
    cursor.execute("INSERT INTO benutzer (name) VALUES (?)", ("Max Mustermann",))
    aktuelle_nutzer_id = cursor.lastrowid

    start_date = datetime(2026, 1, 1)

    # Einträge (Trainings) generieren
    for i in range(num_entries):
        typ = random.choice(["Krafttraining", "Dauerlauf", "Sprint"])
        datum = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        uhrzeit = "18:00"

        if typ == "Dauerlauf":
            # Grenzfall Extremewerte: Alle 25 Durchläufe ein Tippfehler bei der Distanz
            if random.random() < 0.04:
                distanz_km = 45.0
            else:
                distanz_km = 5.0 + (i * 0.05) + random.uniform(-0.2, 0.2)

            wertung = round(distanz_km * 12, 2)

            # Dauer gekoppelt an die Leistung (mit Zufall)
            base_duration = 35 + (wertung * 0.4)
            dauer_min = int(base_duration + random.randint(-5, 5))

            cursor.execute(
                "INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung) VALUES (?,?,?,?,?,?)",
                (aktuelle_nutzer_id, typ, datum, uhrzeit, dauer_min, wertung),
            )
            t_id = cursor.lastrowid

            # Generierung der mittleren Herzfrequenz
            # Grenzfall: Alle 20 Durchläufe ist hf_mittel None (keine Eingabe durch Nutzer erfolgt)
            hf = None if (i > 0 and i % 20 == 0) else random.randint(140, 160)

            cursor.execute(
                "INSERT INTO dauerlauf_details (training_id, distanz_km, hf_mittel) VALUES (?,?,?)",
                (t_id, round(distanz_km, 2), hf),
            )

        elif typ == "Sprint":

            anzahl = random.randint(6, 12)
            base_speed = 25.0 + (i * 0.15)  # Höchstgeschwindigkeit mit natürlicher Streuung (Tagesform)
            max_geschw = base_speed + random.uniform(-0.5, 0.5)
            wertung = round((anzahl * max_geschw) / 4.0, 2)
            base_duration = 10 + (anzahl * 2.5)
            dauer_min = int(base_duration + random.randint(-2, 2))

            cursor.execute(
                "INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung) VALUES (?,?,?,?,?,?)",
                (aktuelle_nutzer_id, typ, datum, uhrzeit, dauer_min, wertung),
            )
            t_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO sprint_details (training_id, anzahl, max_kmh) VALUES (?,?,?)",
                (t_id, anzahl, round(max_geschw, 1)),
            )

        elif typ == "Krafttraining":
            uebungen = [("Kniebeugen", 60), ("Bankdrücken", 50), ("Kreuzheben", 80)]
            gesamtvolumen = 0
            detail_inserts = []

            # Grenzfall: Alle 30 Durchläufe ein ungültiger Eintrag (0 Wiederholungen)
            is_corrupted = (i > 0 and i % 30 == 0)

            for name, basis in uebungen:
                progression = _calculate_natural_progression(i)
                gewicht = round(basis + progression, 1)
                saetze = 3
                wdh = 0 if is_corrupted else 10

                gesamtvolumen += gewicht * saetze * wdh
                detail_inserts.append((name, saetze, wdh, gewicht))

            wertung = round(gesamtvolumen / 20, 2)

            # Wenn der Eintrag korrumpiert ist (Wertung=0), war es ein kurzes Fehl-Training (15 Min)
            if is_corrupted:
                dauer_min = 15
            else:
                base_duration = 45 + (wertung * 0.15)
                dauer_min = int(base_duration + random.randint(-5, 5))

            cursor.execute(
                "INSERT INTO trainings (nutzer_id, typ, datum, uhrzeit, dauer_min, wertung) VALUES (?,?,?,?,?,?)",
                (aktuelle_nutzer_id, typ, datum, uhrzeit, 60, wertung),
            )
            t_id = cursor.lastrowid

            for name, saetze, wdh, gewicht in detail_inserts:
                cursor.execute(
                    "INSERT INTO krafttraining_uebungen (training_id, name, saetze, wdh, gewicht) VALUES (?,?,?,?,?)",
                    (t_id, name, saetze, wdh, gewicht),
                )

    conn.commit()
    # Verhindern, dass während eines Tests die Verbindung geschlossen wird:
    if not isinstance(db_path, sqlite3.Connection):
        conn.close()


if __name__ == "__main__":
    generate_data()
