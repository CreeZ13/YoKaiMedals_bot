from core.db_manager._connection import DatabaseConnection

class CheckData:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.conn = self.db_connection.connect()
        self.yokai_list = self.db_connection.get_yokai_list()

    def _execute_query(self, query: str, params: tuple = ()) -> bool:
        """Esegue la query in sicurezza e ritorna True se esiste almeno un risultato."""
        try:
            with self.conn:  # gestisce commit/rollback automatico
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f"[CheckData] Errore query: {e}")
            return False

    def check_user_has_yokai(self, user_id: str, chat_id: str) -> bool:
        query = "SELECT 1 FROM yokaidata WHERE user_id = ? AND chat_id = ? LIMIT 1"
        return self._execute_query(query, (user_id, chat_id))

    def check_chat_id_exists(self, chat_id: str) -> bool:
        query = "SELECT 1 FROM chats WHERE chat_id = ? LIMIT 1"
        return self._execute_query(query, (chat_id,))

    def check_user_id_exists(self, user_id: str) -> bool:
        query = "SELECT 1 FROM users WHERE user_id = ? LIMIT 1"
        return self._execute_query(query, (user_id,))

    def check_user_username_exists(self, username: str) -> bool:
        query = "SELECT 1 FROM users WHERE username = ? LIMIT 1"
        return self._execute_query(query, (username,))

    def check_user_has_items(self, user_id: str, chat_id: str) -> bool:
        query = "SELECT 1 FROM items WHERE user_id = ? AND chat_id = ? AND kai != 0 LIMIT 1"
        return self._execute_query(query, (user_id, chat_id))

    def check_chat_in_check_mess(self, chat_id: str) -> bool:
        query = "SELECT 1 FROM check_mess WHERE chat_id = ? LIMIT 1"
        return self._execute_query(query, (chat_id,))

    def check_chat_in_yokai_spawned_data(self, chat_id: str) -> bool:
        query = "SELECT 1 FROM yokai_spawned_data WHERE chat_id = ? LIMIT 1"
        return self._execute_query(query, (chat_id,))

    def check_yokaiName_in_yokaiList(self, yokai_name: str, chat_language: str) -> bool:
        for yokai in self.yokai_list:
            if yokai.get(chat_language, "").lower() == yokai_name.lower():
                return True
        return False
