from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.writedata import WriteData


class YkgiftCommand:
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
        # Recupera il testo dopo il comando (/ykgift o /ykgift@botusername)
        message_text = update.message.text or ""
        parts = message_text.split(maxsplit=1)
        if len(parts) > 1:
            self.message_text = parts[1].strip()
        else:
            self.message_text = ""

    async def ykgift(self, update: Update, context: CallbackContext):
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

        # Se la struttura del messaggio non è corretta, mostra la guida
        message_text_parts = self.message_text.strip().split(maxsplit=1)
        if len(message_text_parts) < 2:
            await update.message.reply_text(
                text=self.config.get_text('ykgiftguide', self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Divide il messaggio nelle sue due parti: destinatario e yokai
        recipient_username = message_text_parts[0][1:]   # Rimuove il '@' iniziale
        yokai_name = message_text_parts[1].lower() if len(message_text_parts) > 1 else None

        # Verifica se l'id del destinatario esiste nel DB
        recipient_id = self.getData.get_user_id_from_username(recipient_username)
        if recipient_id is None:
            await update.message.reply_text(
                self.config.get_text("recipientnotfound", self.language),
                parse_mode=ParseMode.HTML, do_quote=True
            )
            return

        # Verifica se lo yokai scritto nel messaggio esiste nel json
        yokai_id = self.getData.get_yokai_id_from_name(yokai_name)
        if yokai_id is None:
            await update.message.reply_text(
                self.config.get_text("yokainotfound", self.language),
                parse_mode=ParseMode.HTML, do_quote=True
            )
            return

        # Verifica se l'utente ha lo yokai da regalare
        owned_yokai_ids = self.getData.get_yokai_ids_collected(self.user_id, self.chat_id)
        if yokai_id not in owned_yokai_ids:
            await update.message.reply_text(
                self.config.get_text("yokainotgot", self.language),
                parse_mode=ParseMode.HTML, do_quote=True
            )
            return
        
        # Effettua lo scambio e comunica in chat
        self.writeData.remove_yokai_from_user(self.user_id, self.chat_id, int(yokai_id))
        self.writeData.add_yokai_to_user(recipient_id, self.chat_id, int(yokai_id))

        await update.message.reply_text(
            f"<i>Yo-Kai: <b>{yokai_name.capitalize()}</b> {self.config.get_text('ykgiftdone', self.language)}</i>\n"
            f"@{self.user_username} ---> @{recipient_username}\n",
            parse_mode=ParseMode.HTML, 
            do_quote=False
        )
