# test_db_connection.py

import sqlite3
import pandas as pd


def test_db_content():
    # Verbindung zur generierten DB
    conn = sqlite3.connect("data/fitness_mock.db")

    # Test-Abfrage
    df_test = pd.read_sql_query(
        "SELECT typ, COUNT(*) as anzahl FROM trainings GROUP BY typ", conn
    )

    # Ein 'assert' ist für pytest zwingend, um den Erfolg zu prüfen
    assert not df_test.empty
    assert "typ" in df_test.columns

    conn.close()
