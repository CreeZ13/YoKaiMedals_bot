from core.db_manager._connection import DatabaseConnection

class GetData:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.conn = self.db_connection.connect()
        self.cursor = self.conn.cursor()
        self.yokai_list = self.db_connection.get_yokai_list()
        self.legendaries = self.db_connection.get_legendaries()

    # Restituisce la lingua settata per una chat se esiste, altrimenti None
    def get_language(self, chat_id: str) -> str | None:
        query = "SELECT language FROM chats WHERE chat_id = ?"
        self.cursor.execute(query, (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Restituisce lo spawn_range settato per una chat se esiste, altrimenti None
    def get_spawnrange(self, chat_id: str) -> str | None:
        query = "SELECT spawnrange FROM chats WHERE chat_id = ?"
        self.cursor.execute(query, (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Restituisce un dizionario con tutte le colonne della tabella chats per la chat_id
    def get_chat_info(self, chat_id: str) -> dict | None:
        query = "SELECT * FROM chats WHERE chat_id = ?"
        self.cursor.execute(query, (chat_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        # Recupero nomi delle colonne dalla descrizione del cursore
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    # Restituisce un dizionario con user_id e current_page dalla tabella medallium_pages
    def get_medallium_pages_data(self, message_id: str, chat_id: str) -> dict | None:
        query = """
            SELECT user_id, current_page, sort_mode
            FROM medallium_pages
            WHERE message_id = ? AND chat_id = ?
        """
        self.cursor.execute(query, (message_id, chat_id))
        row = self.cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    # Restituisce un dizionario con user_id e current_page dalla tabella seals_pages
    def get_seals_pages_data(self, message_id: str, chat_id: str) -> dict | None:
        query = """
            SELECT user_id, current_page
            FROM seals_pages
            WHERE message_id = ? AND chat_id = ?
        """
        self.cursor.execute(query, (message_id, chat_id))
        row = self.cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    # Restituisce il message_id del medallium aperto per una chat e un utente oppure None se non esiste
    def get_message_id_from_medallium_pages(self, chat_id: str, user_id: str) -> str | None:
        self.cursor.execute(
            """
            SELECT message_id
            FROM medallium_pages
            WHERE chat_id = ? AND user_id = ?
            LIMIT 1
            """,
            (chat_id, user_id)
        )
        row = self.cursor.fetchone()
        if row:
            return str(row[0])
        return None
    
    # Restituisce il message_id dei sigilli aperti per una chat e un utente oppure None se non esiste
    def get_message_id_from_seals_pages(self, chat_id: str, user_id: str) -> str | None:
        self.cursor.execute(
            """
            SELECT message_id
            FROM seals_pages
            WHERE chat_id = ? AND user_id = ?
            LIMIT 1
            """,
            (chat_id, user_id)
        )
        row = self.cursor.fetchone()
        if row:
            return str(row[0])
        return None

    # Restituisce un dizionario con i dati da check_mess per la chat_id
    def get_check_mess_data(self, chat_id: str) -> dict | None:
        query = """
            SELECT current_mess_count, stop_mess_count, is_yokai_spawned
            FROM check_mess
            WHERE chat_id = ?
        """
        self.cursor.execute(query, (chat_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    # Restituisce un dizionario con i dati da yokai_spawned_data per la chat_id
    def get_yokai_spawned_data(self, chat_id: str) -> dict | None:     
        query = """
            SELECT yokai_id, current_mess_limit, max_mess_limit, current_friend_limit, max_friend_limit
            FROM yokai_spawned_data
            WHERE chat_id = ?
        """
        self.cursor.execute(query, (chat_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    # Dato il nome di uno yokai (in qualunque lingua), restituisce l'id corrispondente o None
    def get_yokai_id_from_name(self, yokai_name: str) -> str | None:
        yokai_name_lower = yokai_name.lower()
        for yokai in self.yokai_list:
            # Controlla solo i campi delle lingue
            for lang in ["en", "it"]:
                if lang in yokai and yokai[lang].lower() == yokai_name_lower:
                    return yokai.get("id")
        return None

    # Dato uno yokai_id, restituisce un dizionario {lang_code: nome} corrispondente
    def get_yokai_name_from_id(self, yokai_id: str, lang_key: str) -> str:
        for yokai in self.yokai_list:
            if yokai["id"] == yokai_id:
                return yokai[lang_key]  # accesso diretto, errore se lang non esiste
        return None
    
    # Restituisce un dizionario con i dati di uno yokai specifico dato il suo id
    def get_yokai_info(self, yokai_id: str) -> dict | None:
        for yokai in self.yokai_list:
            if yokai.get("id") == yokai_id:
                return yokai
        return None
    
    # Restituisce una lista di id yokai che hanno un certo rank
    def get_yokai_ids_by_rank(self, rank: str) -> list[str]:
        yokai_list = self.yokai_list  # recupera la lista di dizionari
        valid_ids = []
        for yokai in yokai_list:
            if not yokai:
                continue  # salta eventuali elementi None
            yokai_rank = yokai.get("rank")
            if yokai_rank and yokai_rank.lower() == rank.lower():
                valid_ids.append(str(yokai.get("id")))
        return valid_ids

    # Restituisce una lista di id yokai che sono di una certa tribu
    def get_yokai_ids_by_coin(self, coin: str) -> list[str]:
        yokai_list = self.yokai_list  # recupera la lista di dizionari
        valid_ids = []
        for yokai in yokai_list:
            if not yokai:
                continue  # salta eventuali elementi None
            yokai_rank = yokai["coin"]
            if yokai_rank and yokai_rank.lower() == coin.lower():
                valid_ids.append(str(yokai.get("id")))
        return valid_ids
    
    # Restituisce l'user_id associato a un username, o None se non esiste
    def get_user_id_from_username(self, username: str) -> str | None:
        query = "SELECT user_id FROM users WHERE user_username = ?"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # Restituisce un dizionario con user_username e user_fullname per un user_id
    def get_user_info(self, user_id: str) -> dict | None:
        query = "SELECT user_username, user_fullname FROM users WHERE user_id = ?"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {"user_username": result[0], "user_fullname": result[1]}
        return None
    
    # Restituisce una lista di tutti gli user_id presenti nella tabella users
    def get_all_users(self):
        query = "SELECT user_id FROM users"
        self.cursor.execute(query)
        users = [row[0] for row in self.cursor.fetchall()]
        return users

    # Restituisce una lista di yokai_id raccolti da un utente in una chat
    def get_yokai_ids_collected(self, user_id: str, chat_id: str) -> list[str]:
        query = """
            SELECT yokai_id FROM yokaidata
            WHERE user_id = ? AND chat_id = ?
        """
        self.cursor.execute(query, (user_id, chat_id))
        return [str(row[0]) for row in self.cursor.fetchall()]
    
    # Restituisce un dizionario con i conteggi di yokai per ogni utente in una chat (serve per /leaderboard)
    def get_yokai_count_by_user_in_chat(self, chat_id: str) -> dict:
        query = """
            SELECT user_id, COUNT(*) 
            FROM yokaidata
            WHERE chat_id = ?
            GROUP BY user_id
        """
        self.cursor.execute(query, (chat_id,))
        results = self.cursor.fetchall()
        data = {}
        for row in results:
            user_id = row[0]
            count = row[1]
            data[user_id] = count
        return data

    # Conta quanti utenti distinti in questa chat possiedono almeno una volta lo yokai_id.
    # I duplicati dello stesso utente non vengono contati.
    def get_yokai_owners_count_in_group(self, yokai_id: str, chat_id: str) -> int:
        query = "SELECT user_id, yokai_id FROM yokaidata WHERE chat_id = ?"
        self.cursor.execute(query, (chat_id,))
        results = self.cursor.fetchall()
        owners_set = set()
        for user_id, yokai_ids in results:
            if not yokai_ids:
                continue
            yokai_list = str(yokai_ids).split(",")
            if str(yokai_id) in yokai_list:
                owners_set.add(user_id)
        return len(owners_set)
    
    # Ritorna il numero totale di volte in cui lo yokai_id è presente nel database,
    # considerando tutti gli utenti e tutte le chat. I duplicati contano in questo caso.
    # Serve per il comando /flex
    def get_global_yokai_count(self, yokai_id: str) -> int:
        query = "SELECT yokai_id FROM yokaidata"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        total_count = 0
        for (yokai_ids,) in results:
            if yokai_ids is None:
                continue
            if int(yokai_ids) == int(yokai_id):  # confronto diretto
                total_count += 1
        return total_count

    # Restituisce il conteggio di kai per un utente in una chat
    def get_kai(self, user_id: str, chat_id: str) -> int:
        query = "SELECT kai FROM items WHERE user_id = ? AND chat_id = ?"
        self.cursor.execute(query, (user_id, chat_id))
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    # Restituisce la lista degli id degli yokai leggendari di yokai_list
    def get_legendary_yokai_ids(self) -> list[str]:
        yokai_ids = []
        for legendary in self.legendaries:
            yokai_ids.append(legendary["yokai_id"])
        return yokai_ids
    
    # Restituisce la lista degli id degli yokai richiesti di un sigillo leggendario dato l'id dello yokai di yokai_list
    def get_legendary_requirements_ids_from_yokaiID(self, yokai_id: str) -> list[str]:
        for legendary in self.legendaries:
            if legendary["yokai_id"] == yokai_id:
                return legendary["requirements_ids"]

    # Restituisce la lista degli id degli yokai richiesti di un sigillo leggendario dato l'id assoluto del sigillo (da 1 a 15)
    def get_legendary_requirements_ids_from_legendaryID(self, legendary_id: str) -> list[str]:
        for legendary in self.legendaries:
            if legendary["legendary_id"] == legendary_id:
                return legendary["requirements_ids"]       
    
    # Restituisce la lista di tutti gli id degli yokai richiesti da tutti i sigilli leggendari 
    # (serve per controllare se uno yokai da regalare è tra quelli dei sigilli)
    def get_every_requirements_seals_ids(self) -> list[str]:
        requirements_ids = []
        for legendary in self.legendaries:
            requirements_ids.extend(legendary["requirements_ids"])
        return requirements_ids
    
    # Restituisce lo yokai_id di yokai_list a partire dal legendary_id di legendaries.json
    def get_yokai_id_from_legendary_id(self, legendary_id: str) -> str | None:
        for legendary in self.legendaries:
            if legendary["legendary_id"] == legendary_id:
                return legendary["yokai_id"]
        return None

    # Restituisce il numero di leggendari posseduti da un utente in una chat
    def get_number_of_legendaries_owned(self, user_id: str, chat_id: str) -> int:
        owned_yokai_ids = self.get_yokai_ids_collected(user_id, chat_id)
        legendary_ids = self.get_legendary_yokai_ids()
        count = 0
        for yokai_id in owned_yokai_ids:
            if yokai_id in legendary_ids:
                count += 1
        return count
                
