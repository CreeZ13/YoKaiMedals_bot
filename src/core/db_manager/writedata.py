from core.db_manager._connection import DatabaseConnection

class WriteData:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.conn = self.db_connection.connect()
        self.cursor = self.conn.cursor()
        self.yokai_list = self.db_connection.get_yokai_list()

    def _execute(self, query: str, params: tuple):
        self.cursor.execute(query, params)
        self.conn.commit()

    # -- ADDING METHODS -- #

    def add_user(self, user_id: str, user_username: str, user_fullname: str):
        query = """
        INSERT OR REPLACE INTO users (user_id, user_username, user_fullname)
        VALUES (?, ?, ?)
        """
        self._execute(query, (user_id, user_username, user_fullname))

    def add_chat(self, chat_id: str, chat_username: str, chat_fullname: str):
        query = """
        INSERT OR REPLACE INTO chats (chat_id, chat_username, chat_fullname)
        VALUES (?, ?, ?)
        """
        self._execute(query, (chat_id, chat_username, chat_fullname))

    def add_yokai_to_user(self, user_id: str, chat_id: str, yokai_id: int):
        query = """
        INSERT INTO yokaidata (user_id, chat_id, yokai_id)
        VALUES (?, ?, ?)
        """
        self._execute(query, (user_id, chat_id, yokai_id))

    def add_check_mess(self, chat_id: str, stop_mess_count: int):
        query = """
        INSERT OR IGNORE INTO check_mess (chat_id, stop_mess_count)
        VALUES (?, ?)
        """
        self._execute(query, (chat_id, stop_mess_count))

    def add_yokai_spawned_data(self, chat_id: str, yokai_id: str, max_mess_limit: int, max_friend_limit: int):
        query = """
        INSERT OR IGNORE INTO yokai_spawned_data (
            chat_id, yokai_id, max_mess_limit, max_friend_limit
        ) VALUES (?, ?, ?, ?)
        """
        self._execute(query, (chat_id, yokai_id, max_mess_limit, max_friend_limit))

    def add_medallium_page(self, message_id: str, chat_id: str, user_id: str):
        query = """
        INSERT OR IGNORE INTO medallium_pages (message_id, chat_id, user_id)
        VALUES (?, ?, ?)
        """
        self._execute(query, (message_id, chat_id, user_id))

    def add_seals_page(self, message_id: str, chat_id: str, user_id: str):
        query = """
        INSERT OR IGNORE INTO seals_pages (message_id, chat_id, user_id)
        VALUES (?, ?, ?)
        """
        self._execute(query, (message_id, chat_id, user_id))

    def add_items(self, user_id: str, chat_id: str, kai: int):
        query = """
        INSERT OR IGNORE INTO items (user_id, chat_id, kai)
        VALUES (?, ?, ?)
        """
        self._execute(query, (user_id, chat_id, kai))

    # -- REMOVING METHODS -- #

    def remove_yokai_from_user(self, user_id: str, chat_id: str, yokai_id: int):
        query = """
        DELETE FROM yokaidata 
        WHERE rowid IN (
            SELECT rowid FROM yokaidata
            WHERE user_id = ? AND chat_id = ? AND yokai_id = ?
            LIMIT 1
        )
        """
        self._execute(query, (user_id, chat_id, yokai_id))

    def remove_yokai_spawned_data(self, chat_id: str):
        query = "DELETE FROM yokai_spawned_data WHERE chat_id = ?"
        self._execute(query, (chat_id,))

    def remove_medallium_page(self, chat_id: str, user_id: str):
        query = "DELETE FROM medallium_pages WHERE chat_id = ? AND user_id = ?"
        self._execute(query, (chat_id, user_id))
    
    def remove_seals_page(self, chat_id: str, user_id: str):
        query = "DELETE FROM seals_pages WHERE chat_id = ? AND user_id = ?"
        self._execute(query, (chat_id, user_id))

    def remove_check_mess(self, chat_id: str):
        query = "DELETE FROM check_mess WHERE chat_id = ?"
        self._execute(query, (chat_id,))

        