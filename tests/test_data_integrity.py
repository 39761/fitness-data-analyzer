# test_data_integrity.py

import sqlite3


def test_krafttraining_wertung_logic():
    """
    Prüft, ob die Wertung beim Krafttraining korrekt als (Volumen / 20) berechnet wurde.
    """
    conn = sqlite3.connect("data/fitness_mock.db")
    cursor = conn.cursor()

    # Wir holen uns das berechnete Gesamtvolumen pro Training aus den Details
    # und vergleichen es mit der Wertung in der Haupttabelle
    query = """
    SELECT 
        t.id, 
        t.wertung, 
        SUM(k.saetze * k.wdh * k.gewicht) / 20.0 as berechnete_wertung
    FROM trainings t
    JOIN krafttraining_uebungen k ON t.id = k.training_id
    WHERE t.typ = 'Krafttraining'
    GROUP BY t.id
    """

    cursor.execute(query)
    results = cursor.fetchall()

    for t_id, gespeicherte_wertung, berechnete_wertung in results:
        # Wir runden auf 2 Stellen, da wir das auch im Generator getan haben
        expected = round(berechnete_wertung, 2)

        assert (
            gespeicherte_wertung == expected
        ), f"Fehler bei Training ID {t_id}: Erwartet {expected}, gefunden {gespeicherte_wertung}"

    conn.close()
