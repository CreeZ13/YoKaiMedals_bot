from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.writedata import WriteData
from core.db_manager.checkdata import CheckData

class InventoryCommand:
    def __init__(self):  
        self.config = Config()
        self.getData = GetData()
        self.writeData = WriteData()
        self.checkData = CheckData()

    def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)
        self.user_username = update.effective_user.username
        self.language = self.getData.get_language(self.chat_id)

    async def inventory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text(text=self.config.get_text("onlyingroups", "en"), 
                                            parse_mode=ParseMode.HTML, 
                                            do_quote=True)
            return      
        # Prende i dati contestuali
        self._set_context_data(update)
        # Aggiungi items se non esiste il record
        user_has_items_record = self.checkData.check_user_has_items(self.user_id, self.chat_id)
        if not user_has_items_record:
            self.writeData.add_items(self.user_id, self.chat_id, 0)
        
        # Recupera gli kai dell'utente e comunica
        kai = self.getData.get_kai(self.user_id, self.chat_id)
        
        await update.message.reply_text(
            text=f"@{self.user_username}{self.config.get_text('showinventory', self.language)[0]}\n\n"
                f"{self.config.get_text('showinventory', self.language)[1]} <b>{kai}</b>",
            parse_mode=ParseMode.HTML,
            do_quote=True
            )
