# Yo-Kai Medals Telegram Bot

Un bot Telegram completo e modulare per la gestione di un collezionabile game dedicato agli Yo-Kai, con elementi da gacha, raccolta, classifica, inventario e molto altro.

---

## 📁 Struttura del Progetto

```
C:│   main.py
│   requirements.txt
│
├───config
│       admins.yml
│       bot.yml
│       config.py
│       texts.yml
│       urls.yml
│
├───core
│   ├───bot
│   │   │   admin.py
│   │   │   callbacks_handler.py
│   │   │   keyboards.py
│   │   │   message_handlers.py
│   │   │   setup.py
│   │   │   __init__.py
│   │   │
│   │   └───command_handlers
│   │           basic.py
│   │           friend.py
│   │           gift.py
│   │           inventory.py
│   │           leaderboard.py
│   │           medallium.py
│   │           release.py
│   │           slotkai.py
│   │           __init__.py
│   │
│   └───db_manager
│       │   checkdata.py
│       │   getdata.py
│       │   updatedata.py
│       │   writedata.py
│       │   _connection.py
│       │   __init__.py
│       
│       
├───data
│       database.db
│       schema.sql
│       yokai_list.json
│
├───resources
│   ├───other_images
│   │       botpic.png
│   │       crank-a-kai.png
│   │
│   └───yokai_images
│           1.png
│           ... (altre immagini yokai)
│
└───_backups
        new_database_PRESET.db
        OLD_DATABASE.db
```


## 🛠 Tecnologie Usate

- **Python 3.11+**
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** `v20+`
- **SQLite3** per la persistenza dei dati
- **PyYAML** per file di configurazione

---

## 📌 Funzionalità Principali

### 👥 Gestione Utenti e Gruppi

- Salvataggio automatico dei nuovi utenti che entrano nei gruppi
- Registrazione automatica del bot appena viene aggiunto
- Controllo dei messaggi e spawn automatico di Yo-Kai

### 🌀 Yo-Kai Spawn System

- Sistema di generazione casuale con probabilità configurabili
- Sistema `check_mess` con soglia random per spawn
- Classificazione Yo-Kai per rank (E, D, C, B, A, S)

### 🎰 Crankakai (Slotkai)

- Estrazione random Yo-Kai tramite comando `/crankakai`
- Kai (valuta) necessaria per usare il crankakai

### 🎁 Sistema Gifting

- Possibilità di regalare Yo-Kai ad altri utenti
- Gestione inventario oggetti

### 📘 Medallium

- Catalogo personale dei propri Yo-Kai ottenuti
- Navigazione con tastiere inline

### 🏆 Leaderboard

- Classifica per numero di Yo-Kai raccolti per chat

### 🔧 Settings e Lingua

- Comando `/settings` per cambiare lingua e opzioni
- Multilingua supportato (IT / EN)

### 🛡 Comandi Admin

- `/addkai @utente N` per aggiungere valuta kai
- `/addyokai @utente nome_yokai` per assegnare un determinato Yo-Kai

---

## ⚙️ Database

### Tabelle principali:

- `users`: ID utente, username, fullname
- `chats`: ID chat, username gruppo, titolo
- `check_mess`: controllo messaggi per trigger spawn
- `yokai_spawned_data`: dati relativi allo yokai spawnato nel gruppo
- `items`: valuta kai per utente/chat
- `medallium_pages`: pagina attuale del medallium per utente
- `yokaidata`: lista yokai ottenuti da ogni utente in ogni gruppo

> Nota: La lista base degli yokai (`yokailist`) si trova in `data/yokai_list.json`

---

## 🔐 Admins

- Gli ID degli admin abilitati all’uso dei comandi riservati sono salvati in `config/admins.yml`

---

## 🚀 Avvio del Bot

1. Imposta i file `bot.yml`, `texts.yml`, `urls.yml`, `admins.yml`
2. Avvia il file `main.py`
3. Il bot si connetterà tramite token e registrerà automaticamente gli eventi e i comandi

---

## 📄 Licenza e Autore

Bot realizzato da @CreeZ13 (su telegram e github), progettato per essere modulare, chiaro e scalabile.
Nessuna licenza aperta dichiarata (uso privato o personale).

