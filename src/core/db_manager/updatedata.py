from core.db_manager._connection import DatabaseConnection

class UpdateData:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.conn = self.db_connection.connect()
        self.cursor = self.conn.cursor()
        self.yokai_list = self.db_connection.get_yokai_list()

    def _execute(self, query: str, params: tuple):
        self.cursor.execute(query, params)
        self.conn.commit()


    def set_language(self, chat_id: str, lang_key: str):
        query = "UPDATE chats SET language = ? WHERE chat_id = ?"
        self._execute(query, (lang_key, chat_id))

    def set_spawnrange(self, chat_id: str, spawnrange: str):
        query = "UPDATE chats SET spawnrange = ? WHERE chat_id = ?"
        self._execute(query, (spawnrange, chat_id))

    def update_current_medallium_page(self, chat_id: str, message_id: str, delta: int):
        query = """
        UPDATE medallium_pages
        SET current_page = current_page + ?
        WHERE chat_id = ? AND message_id = ?
        """
        self._execute(query, (delta, chat_id, message_id))

    def update_current_seals_page(self, chat_id: str, message_id: str, delta: int):
        query = """
        UPDATE seals_pages
        SET current_page = current_page + ?
        WHERE chat_id = ? AND message_id = ?
        """
        self._execute(query, (delta, chat_id, message_id))

    def update_sort_mode(self, chat_id: str, message_id: str, sort_mode: str):
        query = """
        UPDATE medallium_pages
        SET sort_mode = ?
        WHERE chat_id = ? AND message_id = ?
        """
        self._execute(query, (sort_mode, chat_id, message_id))

    def set_yokai_spawned_true(self, chat_id: str):
        query = "UPDATE check_mess SET is_yokai_spawned = 'True' WHERE chat_id = ?"
        self._execute(query, (chat_id,))

    def set_yokai_spawned_false(self, chat_id: str):
        query = "UPDATE check_mess SET is_yokai_spawned = 'False' WHERE chat_id = ?"
        self._execute(query, (chat_id,))

    def update_kai(self, user_id: str, chat_id: str, delta: int):
        query = """
        UPDATE items
        SET kai = kai + ?
        WHERE user_id = ? AND chat_id = ?
        """
        self._execute(query, (delta, user_id, chat_id))

    def increment_message_count(self, chat_id: str):
        query = "UPDATE check_mess SET current_mess_count = current_mess_count + 1 WHERE chat_id = ?"
        self._execute(query, (chat_id,))

    def increment_mess_limit(self, chat_id: str):
        query = "UPDATE yokai_spawned_data SET current_mess_limit = current_mess_limit + 1 WHERE chat_id = ?"
        self._execute(query, (chat_id,))

    def increment_friend_limit(self, chat_id: str):
        query = "UPDATE yokai_spawned_data SET current_friend_limit = current_friend_limit + 1 WHERE chat_id = ?"
        self._execute(query, (chat_id,))

    def update_users(self, user_id: str, user_username: str, user_fullname: str):
        query = """
        UPDATE users
        SET user_username = ?, user_fullname = ?
        WHERE user_id = ? AND (user_username != ? OR user_fullname != ?)
        """
        self._execute(query, (user_username, user_fullname, user_id, user_username, user_fullname))

    def update_chats(self, chat_id: str, chat_username: str, chat_fullname: str):
        query = """
        UPDATE chats
        SET chat_username = ?, chat_fullname = ?
        WHERE chat_id = ? AND (chat_username != ? OR chat_fullname != ?)
        """
        self._execute(query, (chat_username, chat_fullname, chat_id, chat_username, chat_fullname))