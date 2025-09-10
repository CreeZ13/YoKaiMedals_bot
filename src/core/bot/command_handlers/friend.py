from random import randint
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.updatedata import UpdateData
from core.db_manager.writedata import WriteData
from core.db_manager.checkdata import CheckData


class FriendCommand:
    def __init__(self):
        self.getData = GetData()
        self.writeData = WriteData()
        self.updateData = UpdateData()
        self.checkData = CheckData()
        self.config = Config()

    # Inizializza variabili di contesto
    def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)
        self.user_username = update.effective_user.username
        self.language = self.getData.get_language(self.chat_id)
        
        message_text = update.message.text or ""
        parts = message_text.split(maxsplit=1)
        if len(parts) > 1:
            self.message_text = parts[1].strip()
        else:
            self.message_text = ""

    async def friend(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        if update.message.chat.type == "private":
            await update.message.reply_text(text=self.config.get_text("onlyingroups", "en"), 
                                            parse_mode=ParseMode.HTML, 
                                            do_quote=True)
            return     
        # Prende i dati contestuali
        self._set_context_data(update)
        # Interrompi se il messaggio e' vuoto o l'evento di spawn non e' attivo
        is_yokai_spawned = self.checkData.check_chat_in_yokai_spawned_data(self.chat_id)
        if self.message_text == "" or not is_yokai_spawned:
            await update.message.reply_text(
                text=f"{self.config.get_text('friendguide', self.language)}",
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Logica della cattura #
        yokai_id = str(self.getData.get_yokai_spawned_data(self.chat_id)["yokai_id"])
        yokai_name = self.getData.get_yokai_name_from_id(yokai_id, self.language)
        yokai_rank = self.getData.get_yokai_info(yokai_id)["rank"]
        earned_kai = self.config.get_botConfig("rank-kai")[yokai_rank]

        if self.message_text.lower() == yokai_name.lower():
            # Aggiungi yokai in yokaidata e kai in items (se il record esiste in items)
            self.writeData.add_yokai_to_user(self.user_id, self.chat_id, yokai_id)
            
            user_has_items_record = self.checkData.check_user_has_items(self.user_id, self.chat_id)
            if not user_has_items_record:
                self.writeData.add_items(self.user_id, self.chat_id, 0)
            self.updateData.update_kai(self.user_id, self.chat_id, earned_kai)
            # Resetta l'evento di spawn
            self._reset_spawn_event_data()

            # Comunica in chat
            await update.message.reply_text(
                text=f"@{self.user_username} 🤝🏼 <b>{yokai_name.capitalize()}</b><i>{self.config.get_text('yokaifriended', self.language)[0]} {yokai_rank.upper()}{self.config.get_text('yokaifriended', self.language)[1]}{str(earned_kai)}</i>",
                parse_mode=ParseMode.HTML,
                do_quote=True
                )
        else:
            self.updateData.increment_friend_limit(self.chat_id)
            current_friend_limit = self.getData.get_yokai_spawned_data(self.chat_id)["current_friend_limit"]
            max_friend_limit = self.getData.get_yokai_spawned_data(self.chat_id)["max_friend_limit"]
            if current_friend_limit >= max_friend_limit:
                # Resetta l'evento di spawn
                self._reset_spawn_event_data()
                # Comunica in chat
                await update.message.reply_text(
                    text=self.config.get_text("yokaihasescaped", self.language),
                    parse_mode=ParseMode.HTML,
                    do_quote=False
                    )
                             
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
