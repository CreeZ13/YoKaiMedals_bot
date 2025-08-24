
PRAGMA foreign_keys = ON;

-- TABELLA MADRE: CHATS
CREATE TABLE chats (
    chat_id TEXT PRIMARY KEY,
    chat_username TEXT DEFAULT NULL,
    chat_fullname TEXT DEFAULT NULL,
    spawnrange TEXT DEFAULT 'medium',
    language TEXT DEFAULT 'en'
);

-- TABELLA MADRE: USERS
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    user_username TEXT DEFAULT NULL,
    user_fullname TEXT DEFAULT NULL
);

-- CHECK_MESS (dipende da chats)
CREATE TABLE check_mess (
    chat_id TEXT PRIMARY KEY,
    current_mess_count INTEGER DEFAULT 0,
    stop_mess_count INTEGER DEFAULT NULL,
    is_yokai_spawned TEXT DEFAULT 'False',
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);

-- YOKAI_SPAWNED_DATA (dipende da chats)
CREATE TABLE yokai_spawned_data (
    chat_id TEXT PRIMARY KEY,
    yokai_id INTEGER DEFAULT NULL,
    current_mess_limit INTEGER DEFAULT 0,
    max_mess_limit INTEGER DEFAULT NULL,
    current_friend_limit INTEGER DEFAULT 0,
    max_friend_limit INTEGER DEFAULT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);

-- ITEMS (dipende da users e chats)
CREATE TABLE items (
    user_id TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    kai INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);

-- MEDALLIUM_PAGES (dipende da users e chats)
CREATE TABLE medallium_pages (
    message_id TEXT,
    chat_id TEXT,
    user_id TEXT,
    current_page INTEGER DEFAULT 0,
    sort_mode TEXT DEFAULT 'id',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);

-- YOKAIDATA (dipende da users e chats, molti yokai per utente)
CREATE TABLE yokaidata (
    user_id TEXT,
    chat_id TEXT,
    yokai_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);

-- NOTA: yokailist è esterna, in un file JSON statico.
