from random import randint, choice
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.writedata import WriteData
from core.db_manager.updatedata import UpdateData
from core.db_manager.checkdata import CheckData
from core.bot.keyboards import Keyboards


class MessHandlers:
    def __init__(self):
        self.getData = GetData()
        self.writeData = WriteData()
        self.updateData = UpdateData()
        self.checkData = CheckData()
        self.config = Config()
        self.keyboards = Keyboards()

    # Inizializza variabili di contesto
    async def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.chat_username = update.effective_chat.username
        self.chat_fullname = update.effective_chat.title
        self.user_id = str(update.effective_user.id)
        self.user_username = update.effective_user.username
        self.user_fullname = update.effective_user.full_name
    

    async def handle_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Controlla ogni messaggio nel gruppo, verifica che il bot sia admin, e aggiorna i dati nel DB."""
        msg = update.message or update.edited_message
        if not msg or msg.chat.type not in ("group", "supergroup"):
            return
        
        # Prende i dati contestuali
        await self._set_context_data(update)
        
        # Aggiungi o REPLACE info chat nel DB
        is_chat_exists = self.checkData.check_chat_id_exists(self.chat_id)
        if not is_chat_exists:
            # Se la chat non esiste, la aggiunge
            self.writeData.add_chat(
                chat_id=self.chat_id,
                chat_username=self.chat_username,
                chat_fullname=self.chat_fullname
            )
        else:
            # Se la chat esiste, aggiorna le informazioni
            self.updateData.update_chats(
                chat_id=self.chat_id,
                chat_username=self.chat_username,
                chat_fullname=self.chat_fullname
            )
        
        # Aggiungi o REPLACE info utente nel DB
        is_user_exists = self.checkData.check_user_id_exists(self.user_id)
        if not is_user_exists:
            # Se l'utente non esiste, lo aggiunge
            self.writeData.add_user(
                user_id=self.user_id,
                user_username=self.user_username,
                user_fullname=self.user_fullname
            )
        else:
            # Se l'utente esiste, aggiorna le informazioni
            self.updateData.update_users(
                user_id=self.user_id,
                user_username=self.user_username,
                user_fullname=self.user_fullname
            )
        
        # Ottiene lingua e spawnrange della chat adesso che esistono, sicuramente
        self.language = self.getData.get_language(self.chat_id)
        self.spawnrange = self.getData.get_spawnrange(self.chat_id)

        # Aggiungi o IGNORE tutti i dati nella tabella check_mess
        self.writeData.add_check_mess(
            chat_id=self.chat_id,
            stop_mess_count= self._set_stop_mess_count()
        )

        # Incrementa il mess_count della chat se non e' ancora spawnato nulla
        is_yokai_spawned = self.getData.get_check_mess_data(self.chat_id)["is_yokai_spawned"]
        if is_yokai_spawned == "False":
            self.updateData.increment_message_count(self.chat_id)

        # Attiva l'evento di spawn se "current_mess_count" e' uguale a "stop_mess_count"
        current_mess_count = self.getData.get_check_mess_data(self.chat_id)["current_mess_count"]
        stop_mess_count = self.getData.get_check_mess_data(self.chat_id)["stop_mess_count"]

        if current_mess_count >= stop_mess_count and is_yokai_spawned == "False":
            self.updateData.set_yokai_spawned_true(self.chat_id)
            # Aggiungi info in yokai_spawned_data (or ignore se gia' l'evento e' attivo ed esiste il record)
            yokai_id = self._spawn_yokai_randomly()
            max_mess_limit = self._set_max_mess_limit()
            max_friend_limit = self._set_max_friend_limit()
            self.writeData.add_yokai_spawned_data(
                chat_id=self.chat_id,
                yokai_id=yokai_id,
                max_mess_limit=max_mess_limit,
                max_friend_limit=max_friend_limit
            )
            # Comunica in chat
            image_path = os.path.abspath(f"resources/yokai_images/{yokai_id}.png")
            with open(image_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=self.config.get_text("yokaispawnevent", self.language),
                    parse_mode=ParseMode.HTML
                )

        # Se un yokai è già spawnato, aumenta il contatore dei messaggi falliti.
        # Se il limite massimo viene raggiunto, resetta l'evento e segnala la fuga dello yokai.
        if self.checkData.check_chat_in_yokai_spawned_data(self.chat_id):
            self.updateData.increment_mess_limit(self.chat_id)
            yokai_spawned_data = self.getData.get_yokai_spawned_data(self.chat_id)
            if yokai_spawned_data["current_mess_limit"] >= yokai_spawned_data["max_mess_limit"]:
                self._reset_spawn_event_data()
                await context.bot.send_message(
                    chat_id=self.chat_id,
                    text=self.config.get_text("yokaihasescaped", self.language),
                    parse_mode=ParseMode.HTML
                )
            
    async def handle_new_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
            Gestisce l'ingresso di nuovi membri in un gruppo. 
            Se il bot viene aggiunto, registra la chat e invia messaggio di benvenuto. 
            Se entra un utente, registra i suoi dati nel database.
        """
        new_members = update.message.new_chat_members
        chat_id = str(update.effective_chat.id)
        chat_username = update.effective_chat.username
        chat_fullname = update.effective_chat.title

        for member in new_members:
            if member.id == context.bot.id:
                # Il bot è stato aggiunto al gruppo
                self.writeData.add_chat(
                    chat_id=chat_id,
                    chat_username=chat_username,
                    chat_fullname=chat_fullname
                )
                await update.message.reply_text(
                    text=self.config.get_text('botaddedtogroup', 'en'),
                    reply_markup=self.keyboards.get_keyboard(keyboard_name="lang_kb_without_back", lang_key="en"),
                    do_quote=False,
                    parse_mode=ParseMode.HTML
                )
            else:
                # È entrato un normale utente: salviamo i suoi dati
                self.writeData.add_user(
                    user_id=str(member.id),
                    user_username=member.username,
                    user_fullname=member.full_name
                )


    """ Metodi privati per impostare i valori di configurazione """

    # Imposta il numero di messaggi dopo i quali iniziare l'evento di spawn
    def _set_stop_mess_count(self) -> int:
        stop_mess_count = randint(
            self.config.get_botConfig("spawnranges")[self.spawnrange]["min"],
            self.config.get_botConfig("spawnranges")[self.spawnrange]["max"]
        )
        return stop_mess_count
    
    # Imposta il limite massimo di messaggi falliti prima di far fuggire lo yokai
    def _set_max_mess_limit(self) -> int:
        max_mess_limit = randint(
            self.config.get_botConfig("failbefriend")["mess"]["min"],
            self.config.get_botConfig("failbefriend")["mess"]["max"]
        )
        return max_mess_limit

    # Imposta il limite massimo di tentativi /friend prima di far fuggire lo yokai
    def _set_max_friend_limit(self) -> int:
        max_friend_limit = randint(
            self.config.get_botConfig("failbefriend")["cmd"]["min"],
            self.config.get_botConfig("failbefriend")["cmd"]["max"]
        )
        return max_friend_limit
    
    # Estrae un yokai casualmente in base alle probabilità definite nel file di configurazione
    def _spawn_yokai_randomly(self) -> int:
        nprob = randint(1, 100)
        cumulative = 0
        for rank, chance in self.config.get_botConfig("spawn-probabilities").items():
            cumulative += chance
            if nprob <= cumulative:
                yokai_extracted = choice(self.getData.get_yokai_ids_by_rank(rank))
                return int(yokai_extracted)

    # Resetta i dati dell'evento di spawn
    def _reset_spawn_event_data(self) -> None:
        spawnrange = self.getData.get_spawnrange(self.chat_id)
        stop_mess_count = randint(
            self.config.get_botConfig("spawnranges")[spawnrange]["min"],
            self.config.get_botConfig("spawnranges")[spawnrange]["max"]
        )
        self.writeData.remove_yokai_spawned_data(self.chat_id)
        self.writeData.remove_check_mess(self.chat_id)
        self.writeData.add_check_mess(chat_id=self.chat_id, 
                                      stop_mess_count=stop_mess_count
                                      )
        