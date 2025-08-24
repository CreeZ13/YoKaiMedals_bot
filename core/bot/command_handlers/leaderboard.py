from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData

class LeaderboardCommand:
    def __init__(self):
        self.config = Config()
        self.getdata = GetData()

    # Inizializza variabili di contesto
    def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.language = self.getdata.get_language(self.chat_id)

    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text(
                text=self.config.get_text("onlyingroups", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return
        # Imposta le variabili di contesto
        self._set_context_data(update)
        # Recupera i conteggi dei Yokai per gli utenti nel gruppo
        user_yokai_counts = self.getdata.get_yokai_count_by_user_in_chat(self.chat_id)

        # Se non ci sono utenti con Yokai nel gruppo, invia un messaggio di errore
        if not user_yokai_counts:
            await update.message.reply_text(
                text=self.config.get_text("no_leaderboard", self.language),
                parse_mode=ParseMode.HTML,
                do_quote=False
            )
            return

        # Ordina gli utenti in base al conteggio dei Yokai e limita ai primi 10
        sorted_users = sorted(user_yokai_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Genera il messaggio di output della classifica e comunica
        output_mess = self.config.get_text("showleaderboard", self.language) 
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for i, (user_id, count) in enumerate(sorted_users, start=1):
            user_info = self.getdata.get_user_info(user_id)
            user_username = user_info["user_username"]
            user_fullname = user_info["user_fullname"]
            
            identifier = user_username if user_username else user_fullname
            url = f"https://t.me/{identifier}"
            linkhtml = f'<a href="{url}"><i>{identifier}</i></a>'
            if i in medals:
                # Mostra solo la medaglia senza il numero
                output_mess += f"{medals[i]} {linkhtml}:   <b>{count}</b>\n"
            else:
                # Dal quarto in poi mostra numero + link
                output_mess += f"<b>{i})</b> {linkhtml}:   <b>{count}</b>\n"

        await update.message.reply_text(
            output_mess,
            parse_mode=ParseMode.HTML,
            do_quote=False,
            disable_web_page_preview=True
        )
