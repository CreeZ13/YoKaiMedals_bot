import sqlite3
import json
import os

class DatabaseConnection:
    def __init__(self):
        self.db_path = os.getenv("DB_PATH")
        self.yokai_json_path = os.getenv("YOKAI_JSON_PATH")
        self.legendaries_json_path = os.getenv("LEGENDARIES_JSON_PATH")
        self._conn = None

    def connect(self) -> sqlite3.Connection:
        """
        Apre (se non è già aperta) e restituisce la connessione al database.
        """
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            except sqlite3.Error as e:
                print(f"[DatabaseConnection] Errore durante la connessione al DB: {e}")
                raise
        return self._conn

    def get_yokai_list(self) -> list[dict]:
        """Carica la lista degli yokai dal file JSON."""
        try:
            with open(self.yokai_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DatabaseConnection] Errore durante il caricamento di yokai_list.json: {e}")
            return []

    def get_legendaries(self) -> list[dict]:
        """Carica la lista dei leggendari dal file JSON."""
        try:
            with open(self.legendaries_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DatabaseConnection] Errore durante il caricamento di legendaries.json: {e}")
            return []

    def close(self):
        """
        Chiude la connessione al DB.
        """
        if self._conn is not None:
            try:
                self._conn.close()
            except sqlite3.Error as e:
                print(f"[DatabaseConnection] Errore durante la chiusura del DB: {e}")
            finally:
                self._conn = None
