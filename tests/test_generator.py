# test_generator.py

import unittest
import sqlite3
import random
import os

# Wir importieren deine Funktionen (dafür war die __init__.py wichtig!)
from scripts.generate_mock_data import create_tables, generate_data, _calculate_natural_progression


class TestFitnessDb(unittest.TestCase):
    def setUp(self):
        # Erstellt eine temporäre Datenbank im Speicher für den Test
        self.conn = sqlite3.connect(":memory:")
        create_tables(self.conn)

    def test_tables_exist(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn("benutzer", tables)
        self.assertIn("trainings", tables)
        self.assertIn("krafttraining_uebungen", tables)

    def test_natural_progression_math(self):
        """Validates that the biological curve returns valid floats and changes over time."""
        val_day_1 = _calculate_natural_progression(1)
        val_day_50 = _calculate_natural_progression(50)

        # Check if the output is a float
        self.assertIsInstance(val_day_1, float)
        self.assertIsInstance(val_day_50, float)

        # Ensure that it's not a static value (progression is happening)
        self.assertNotEqual(val_day_1, val_day_50)

    def test_data_generation_inserts_rows(self):
        """Überprüft, ob generate_data die Datenbank ohne Absturz mit Werten füllt."""

        # Fixiert die Zufallsauswahl, damit jeder Typ genau einmal erzeugt wird
        test_types = ["Krafttraining", "Dauerlauf", "Sprint"]

        def mock_choice(seq):
            # Wenn die Liste der erwarteten Typen abgefragt wird, nehmen wir die fixen Werte
            if "Krafttraining" in seq:
                return test_types.pop(0) if test_types else seq[0]
            return seq[0]

        # Temporär random.choice mit unserem Mock überschreiben
        original_choice = random.choice
        random.choice = mock_choice

        try:
            # 3 Einträge reichen, da wir garantieren, dass alle 3 Typen drankommen
            generate_data(db_path=self.conn, num_entries=3)
        finally:
            # Den originalen Zufallsgenerator danach wiederherstellen
            random.choice = original_choice

        cursor = self.conn.cursor()

        # Prüft, ob die Trainings-Tabelle Daten enthält
        cursor.execute("SELECT COUNT(*) FROM trainings;")
        trainings_count = cursor.fetchone()[0]

        # Prüft, ob die Krafttrainings-Übungen-Tabelle Daten enthält
        cursor.execute("SELECT COUNT(*) FROM krafttraining_uebungen;")
        exercises_count = cursor.fetchone()[0]

        self.assertGreater(trainings_count, 0, "Die Tabelle 'trainings' sollte nicht leer sein.")
        self.assertGreater(exercises_count, 0, "Die Tabelle 'krafttraining_uebungen' sollte nicht leer sein.")

    def tearDown(self):
        self.conn.close()


if __name__ == "__main__":
    unittest.main()
