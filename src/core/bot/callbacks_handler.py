import os
from random import choice

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.updatedata import UpdateData
from core.db_manager.writedata import WriteData
from core.bot.keyboards import Keyboards

# Importa la classe MedalliumCommand per le funzioni di paging
from core.bot.command_handlers.medallium import MedalliumCommand

class CallbackHandler:
    def __init__(self):
        self.getData = GetData()
        self.writeData = WriteData()
        self.updateData = UpdateData()
        self.config = Config()
        self.keyboards = Keyboards()

    # Inizializza variabili di contesto
    async def _set_context_data(self, update: Update, context: CallbackContext):
        self.query = update.callback_query
        self.query_data = self.query.data
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)
        self.message_id = str(self.query.message.message_id)
        self.user_username = update.effective_user.username
        chat_member = await context.bot.get_chat_member(self.chat_id, self.user_id)
        self.user_status = chat_member.status
        self.language = self.getData.get_language(chat_id=self.chat_id)

    async def handle_callbacks(self, update: Update, context: CallbackContext):
        # Prende i dati contestuali
        await self._set_context_data(update, context)
        
        # gestisci le azioni in base alla querydata
        if self.query_data in ("en", "it"):
            await self._handle_language_selection(context)
        elif self.query_data in ("fast", "medium", "slow"):
            await self._handle_spawnrange_selection(context)
        elif self.query_data in ("red", "yellow", "orange", "blue", "skyblue", "pink", "purple", "green", "one_star", "five_stars", "special"):
            await self._handle_crankakai(context)
        elif self.query_data in ("open_language_setting", "open_spawnranges_setting", "open_contacts_setting", "back_to_settings"):
            await self._handle_settings_navigation(context)
        elif self.query_data == "close_settings":
            await self._handle_settings_close(context)

        elif self.query_data in ("right", "left", "sort_id", "sort_alphabetical"):
            await self._handle_medallium_navigation(update, context)
            
    async def _handle_language_selection(self, context: CallbackContext):
        if self.user_status in ("creator", "administrator"):
            # Aggiorna lingua nel DB
            self.updateData.set_language(
                lang_key=self.query_data, 
                chat_id=self.chat_id)  
            # Invia messaggio nel gruppo
            await self.query.answer(text=self.config.get_text("changedlanguage", self.query_data))
        else:
            await self.query.answer(text=self.config.get_text("noperms", self.language))

    async def _handle_spawnrange_selection(self, context: CallbackContext):
        if self.user_status in ("creator", "administrator"):
            # Aggiorna spawnrange nel DB
            self.updateData.set_spawnrange(
                chat_id=self.chat_id,
                spawnrange=self.query_data
            )
            # Invia messaggio di conferma
            await self.query.answer(text=f"{self.config.get_text('spawnrangechanged', self.language)} {self.query_data.capitalize()}")
        else:
            await self.query.answer(text=self.config.get_text("noperms", self.language))

    async def _handle_crankakai(self, context: CallbackContext):
        coin_to_category = {
        "red": "tribes", "yellow": "tribes", "orange": "tribes", "blue": "tribes",
        "skyblue": "tribes", "pink": "tribes", "purple": "tribes", "green": "tribes",
        "one_star": "onestar", "five_stars": "fivestar-special", "special": "fivestar-special"
        }

        # Info su costi e controllo disponibilita' kai
        category = coin_to_category[self.query_data]
        coin_cost = self.config.get_botConfig("coin-cost")[category]
        user_kai = self.getData.get_kai(self.user_id, self.chat_id)
        if user_kai < coin_cost:
            await self.query.answer(text=self.config.get_text("notenoughkai", self.language))
            return

        # Estrazione yokai disponibile
        yokai_ids = self.getData.get_yokai_ids_by_coin(coin=self.query_data)
        yokai_id = choice(yokai_ids) #premio
        yokai_name = self.getData.get_yokai_name_from_id(yokai_id=yokai_id, lang_key=self.language)

        # Aggiorna DB: rimuove Kai e aggiunge yokai
        self.updateData.update_kai(user_id=self.user_id,
                                   chat_id=self.chat_id,
                                   delta=-coin_cost)
        self.writeData.add_yokai_to_user(user_id=self.user_id,
                                         chat_id=self.chat_id,
                                         yokai_id=yokai_id)

        # Comunica in chat
        image_path = os.path.abspath(f"resources/yokai_images/{yokai_id}.png")
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=self.chat_id,
                photo=photo,
                caption=(
                    f"{self.config.get_text('crankakaiprize', self.language)[0]} "
                    f"<b>{yokai_name.capitalize()}</b>!\n"
                    f"@{self.user_username} {self.config.get_text('crankakaiprize', self.language)[1]}"
                ),
                parse_mode=ParseMode.HTML
            )
        
    async def _handle_settings_navigation(self, context: CallbackContext) -> None:
        # Mappa le query ai testi e tastiere corrispondenti
        responses = {
            "open_language_setting": (
                self.config.get_text("changelang", self.language),
                self.keyboards.get_keyboard(keyboard_name="lang_kb", lang_key=self.language)
            ),
            "open_spawnranges_setting": (
                self.config.get_text("changespawnrange", self.language),
                self.keyboards.get_keyboard(keyboard_name="spawnrange_kb", lang_key=self.language)
            ),
            "open_contacts_setting": (
                self.config.get_text("showcontact", self.language),
                self.keyboards.get_keyboard(keyboard_name="contactsettings_kb", lang_key=self.language)
            ),
            "back_to_settings": (
                self.config.get_text("showsettings", self.language),
                self.keyboards.get_keyboard(keyboard_name="settings_kb", lang_key=self.language)
            )
        }
        
        if self.query_data in responses:
            text, keyboard = responses[self.query_data]
            await self.query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

    async def _handle_settings_close(self, context: CallbackContext) -> None:
        await context.bot.delete_message(
        chat_id=self.chat_id,
        message_id=self.message_id
    )
        

    # ------------------------------------------
    # Gestione query speciale per i right e left button del medallium
    # ------------------------------------------

    async def _handle_medallium_navigation(self, update: Update, context: CallbackContext):
        await self._set_context_data(update, context)
        # Controlla se a sfogliare questo medallium e' lo stesso utente che ha digitato /medallium
        # In sostanza gli utenti non possono sfogliare medallium di altra gente
        owner_id_of_that_medallium = self.getData.get_medallium_pages_data(self.message_id, self.chat_id)["user_id"]
        if self.user_id != owner_id_of_that_medallium:
            await update.callback_query.answer(text=self.config.get_text("noperms", self.language))
            return

        # Calcolo nuova pagina (se si sfoglia (delta = 1 | -1) oppure se si cambia sort_mode (delta = 0))
        if self.query_data == "right":
            delta = 1
        elif self.query_data == "left":
            delta = -1
        elif self.query_data == "sort_id":
            self.updateData.update_sort_mode(self.chat_id, self.message_id, "id")
            delta = 0
        elif self.query_data == "sort_alphabetical":
            self.updateData.update_sort_mode(self.chat_id, self.message_id, "alphabetical")
            delta = 0

        # Creazione della pagina 
        yokai_ids = self.getData.get_yokai_ids_collected(self.user_id, self.chat_id)
        try:
            current_page = self.getData.get_medallium_pages_data(self.message_id, self.chat_id)["current_page"]
        except TypeError:  # se viene premuto sfogliato un medallium vecchio rimasto aperto o non esistente nel DB
            return
        
        # Calcola nuova pagina e genera il messaggio aggiornato
        new_page = current_page + delta
        text, keyboard = MedalliumCommand().render_page(update=update, context=context,
                                                         yokai_ids=yokai_ids, page=new_page)
        self.updateData.update_current_page(self.chat_id, self.message_id, delta)
        
        # Aggiorna il messaggio del bot
        await context.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
