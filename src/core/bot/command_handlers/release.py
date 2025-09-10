from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.writedata import WriteData


class ReleaseCommand:
    def __init__(self):
        self.config = Config()
        self.getData = GetData()
        self.writeData = WriteData()

    # Inizializza variabili di contesto
    def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)
        self.user_username = update.effective_user.username
        self.language = self.getData.get_language(self.chat_id)
        # Recupera il testo dopo il comando (/release o /release@botusername)
        message_text = update.message.text or ""
        parts = message_text.split(maxsplit=1)
        if len(parts) > 1:
            self.message_text = parts[1].strip()
        else:
            self.message_text = ""

    async def release(self, update: Update, context: CallbackContext):
        # Non disponibile in privato
        if update.message.chat.type == "private":
            await update.message.reply_text(
                text=self.config.get_text("onlyingroups", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return
        # Imposta i dati contestuali
        self._set_context_data(update)

        # Se non è stato scritto niente dopo /release (cioe message_text == "")
        if not self.message_text:
            await update.message.reply_text(
                text=self.config.get_text('releaseguide', self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Verifica se lo yokai scritto nel messaggio esiste nel json
        yokai_id = self.getData.get_yokai_id_from_name(self.message_text.lower())
        if yokai_id is None:
            await update.message.reply_text(
                text=self.config.get_text("yokainotfound", self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Verifica se l'utente ha lo yokai da rilasciare
        owned_yokai_ids = self.getData.get_yokai_ids_collected(self.user_id, self.chat_id)
        if yokai_id not in owned_yokai_ids:
            await update.message.reply_text(
                text=self.config.get_text("yokainotgot", self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Effettua il rilascio dello yokai e comunica in chat
        self.writeData.remove_yokai_from_user(self.user_id, self.chat_id, int(yokai_id))
    
        yokai_name = self.getData.get_yokai_name_from_id(yokai_id, self.language).capitalize()    
        await update.message.reply_text(
            text=f"@{self.user_username} {self.config.get_text('releasedone', self.language)} {yokai_name}",
            parse_mode=ParseMode.HTML,
            do_quote=True
        )
