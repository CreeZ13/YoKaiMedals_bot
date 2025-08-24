
# Qui ci sono i comandi di semplici del bot, come /start, /help, /contact /settings e /crankakai.
# cioe' quelli che inviano un solo nemessaggio di risposta diretta

import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.bot.keyboards import Keyboards


class BasicCommands:
    def __init__(self):
        self.getdata = GetData()
        self.config = Config()
        self.keyboards = Keyboards()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type != "private":
            return
        photo_path = os.path.abspath("resources/other_images/botpic.png")
        with open(photo_path, "rb") as botpic:
            await update.message.reply_photo(
                photo=botpic,
                caption=self.config.get_text("startprivate", "en"),
                reply_markup=self.keyboards.get_keyboard("start_kb", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=False
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text(
            self.config.get_text("showguide", "en"),
            reply_markup=self.keyboards.get_keyboard("guide_kb", "en"),
            parse_mode=ParseMode.HTML,
            do_quote=False
        )
            return      
        chat_id = str(update.effective_chat.id)
        lang_key = self.getdata.get_language(chat_id)
        await update.message.reply_text(
            self.config.get_text("showguide", lang_key),
            reply_markup=self.keyboards.get_keyboard("guide_kb", lang_key),
            parse_mode=ParseMode.HTML,
            do_quote=False
        )

    async def contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text(
            self.config.get_text("showcontact", "en"),
            reply_markup=self.keyboards.get_keyboard("contact_kb", "en"),
            parse_mode=ParseMode.HTML,
            do_quote=False
        )
            return
        chat_id = str(update.effective_chat.id)
        lang_key = self.getdata.get_language(chat_id)
        await update.message.reply_text(
            self.config.get_text("showcontact", lang_key),
            reply_markup=self.keyboards.get_keyboard("contact_kb", lang_key),
            parse_mode=ParseMode.HTML,
            do_quote=False
        )

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text(
                self.config.get_text("onlyingroups", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        chat_id = str(update.effective_chat.id)
        user_id = str(update.effective_user.id)
        lang_key = self.getdata.get_language(chat_id)

        # Controllo permessi
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in ("administrator", "creator"):
            await update.message.reply_text(
                self.config.get_text("noperms", lang_key),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return
        
        await update.message.reply_text(
            self.config.get_text("showsettings", lang_key),
            reply_markup=self.keyboards.get_keyboard("settings_kb", lang_key),
            parse_mode=ParseMode.HTML,
            do_quote=True
        )

    async def crankakai(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type == "private":
            await update.message.reply_text(
                self.config.get_text("onlyingroups", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        chat_id = str(update.effective_chat.id)
        lang_key = self.getdata.get_language(chat_id)
        photo_path = os.path.abspath("resources/other_images/crank-a-kai.png")
        with open(photo_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=self.config.get_text("showcrankakai", lang_key),
                reply_markup=self.keyboards.get_keyboard("shopcoins_kb", lang_key),
                parse_mode=ParseMode.HTML,
                do_quote=False
            )
