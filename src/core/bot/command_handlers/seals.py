import os
from PIL import Image
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.writedata import WriteData
from core.db_manager.updatedata import UpdateData
from core.bot.keyboards import Keyboards

''' 
    Il Comando /sigilli ha una struttura molto simile a /medallium, 
    per quanto riguarda la gestione del contesto e la logica di paging.
'''

class SealsCommand:
    def __init__(self):
        self.getdata = GetData()
        self.writedata = WriteData()
        self.updatedata = UpdateData()
        self.config = Config()
        self.keyboards = Keyboards()

    #  Funzione di inizializzazione contesto
    def _set_context_data(self, update: Update, context: CallbackContext):
        if update.message:  # dati presi inviando il comando /seals
            self.message_id = str(update.message.message_id)
            self.chat_id = str(update.message.chat_id)
            self.user_id = str(update.message.from_user.id)
            self.user_username = update.message.from_user.username
        elif update.callback_query:  # dati presi premendo i pulsanti di navigazione
            self.message_id = str(update.callback_query.message.message_id)
            self.chat_id = str(update.callback_query.message.chat_id)
            self.user_id = str(update.callback_query.from_user.id)
            self.user_username = update.callback_query.from_user.username
        self.language = self.getdata.get_language(chat_id=self.chat_id)


    #  Funzione per generare l'immagine del sigillo (quella con la sagoma del leggendario e gli spotlights)
    def _generate_seal_image(self, yokai_id: str, is_unlocked: bool):
        '''
            Ritorna il path dell'immagine generata, oltre a generarla nella
            directory in questione. Poi l'immagine sara eliminata (dunque e' temp)
        '''
        yokai_image_path = os.getenv("RESOURCES_YOKAI_IMAGES_PATH") + f"{yokai_id}.png"
        spotlights_photo_path = os.getenv("RESOURCES_OTHER_IMAGES_PATH") + "spotlights.png"
        temp_file_path = os.getenv("TEMP_PATH") + "seal_image.png"

        # Carica le due immagini: sfondo e yokai (overlay) e prendi le misure
        background = Image.open(spotlights_photo_path).convert("RGBA")
        yokai = Image.open(yokai_image_path).convert("RGBA")
        
        # --- Ridimensiona lo yokai (max 60% dello sfondo) ---
        bg_w, bg_h = background.size
        yk_w, yk_h = yokai.size
        scale_factor = min(bg_w * 0.6 / yk_w, bg_h * 0.6 / yk_h, 1)
        new_size = (int(yk_w * scale_factor), int(yk_h * scale_factor))
        yokai = yokai.resize(new_size, Image.LANCZOS)

        # --- Crea sagoma nera se il sigillo non è ancora sbloccato ---
        if not is_unlocked:
            alpha = yokai.getchannel("A")
            image_to_paste = Image.new("RGBA", yokai.size, (0, 0, 0, 255))
            image_to_paste.putalpha(alpha)
        else:
            image_to_paste = yokai  # usa immagine originale

        # --- Calcola posizione centrale e salva l'immagine ---
        yk_w, yk_h = image_to_paste.size
        x = (bg_w - yk_w) // 2
        y = (bg_h - yk_h) // 2
        background.paste(image_to_paste, (x, y), image_to_paste)
        background.save(temp_file_path, "PNG")  
        return temp_file_path
    

    # ------------------------------
    #   Helpers di paging (riutilizzabili da callbacks)
    # ------------------------------

    # --- Costruisce la PRIMA pagina, quella prima dei sigilli (che mostra le statistiche generali e i sigilli completati)
    def _build_first_page(self, update: Update, context: CallbackContext): 
        self._set_context_data(update, context)  

        NLEGENDARIES = len(self.getdata.get_legendary_yokai_ids()) # (15)
        legendaries_owned = self.getdata.get_number_of_legendaries_owned(self.user_id, self.chat_id)
        message_text = (f"{self.config.get_text('sealsinfo', self.language)[0]} @{self.user_username}\n"
                        f"{self.config.get_text('sealsinfo', self.language)[1]} <b>{legendaries_owned}/{NLEGENDARIES}</b>\n\n"
                        f"{self.config.get_text('sealsinfo', self.language)[2]}")
        keyboard = self.keyboards.get_keyboard("seals_right_kb", self.language)
        return message_text, keyboard

    # --- Costruisce le pagine dei sigilli
    def _build_seals_page(self, update: Update, context: CallbackContext, page: int): 
        self._set_context_data(update, context)  

        owned_yokai_ids = self.getdata.get_yokai_ids_collected(self.user_id, self.chat_id)
        # Ottieni l'id e il nome del leggendario e controlla se lo user_id lo possiede 
        yokai_id = self.getdata.get_legendary_yokai_ids()[page-1]
        yokai_name = self.getdata.get_yokai_name_from_id(yokai_id, self.language).capitalize()
        if yokai_id not in owned_yokai_ids:
            yokai_name = "<b>???</b>"   # Se non posseduto, mostra "???" al posto del nome del leggendario
        message_text = (f"{self.config.get_text('sealsinfo', self.language)[0]} @{self.user_username}\n"
                        f"{self.config.get_text('sealsinfo', self.language)[3]} <b>{yokai_name}</b>\n")

        # Ottieni gli id e i nomi dei yokai richiesti dal sigillo e controlla se lo user_id li possiede (col check verde o la X rossa)
        requirements_ids = self.getdata.get_legendary_requirements_ids_from_yokaiID(yokai_id)
        for yokai_id in requirements_ids:
            yokai_name = self.getdata.get_yokai_name_from_id(yokai_id, self.language).capitalize()
            if yokai_id in owned_yokai_ids:
                message_text += f"\n✔️  <i><b>Yo-Kai: </b>{yokai_name}</i>"
            else:
                message_text += f"\n      <i><b>Yo-Kai: </b>{yokai_name}</i>"       

        # Crea la tastiera di navigazione in base alla pagina attuale
        NPAGE = len(self.getdata.get_legendary_yokai_ids())   # numero totale di pagine dei sigilli (15, cioè il numero di leggendari)
        if page == 0:   # first page
            keyboard = self.keyboards.get_keyboard("seals_right_kb", self.language)
        elif page == NPAGE:   # ultima pagina 
            keyboard = self.keyboards.get_keyboard(f"seals_left_kb", self.language)
        else:   # pagine intermedie 
            keyboard = self.keyboards.get_keyboard(f"seals_rightleft_kb", self.language)
        return message_text, keyboard

    
    # ------------------------------------------
    #   Comando /seals (render_page e' utilizzata anche in callbacks)
    # ------------------------------------------

    # Decidi quale pagina mostrare in base alla current_page
    def render_page(self, update: Update, context: CallbackContext, page: int):
        """
        - page == 0  -> first page con statistiche e sigilli completati
        - page >= 1  -> pagine dei sigilli
        """
        if page == 0:
            return self._build_first_page(update=update, context=context)
        elif page > 0:
            return self._build_seals_page(update=update, context=context, page=page)

    async def seals(self, update: Update, context: CallbackContext):
        # Non disponibile in privato
        if update.message.chat.type == "private":
            await update.message.reply_text(
                text=self.config.get_text("onlyingroups", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return
        self._set_context_data(update, context)

        # Elimina il vecchio messaggio dell' apertura dei sigilli, se esiste
        old_message_id = self.getdata.get_message_id_from_seals_pages(self.chat_id, self.user_id)
        if old_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=self.chat_id,
                    message_id=old_message_id
                )
            except Exception:   # Magari il messaggio era già stato eliminato manualmente
                pass

        # Elimina e reinserisci il corretto record in seals_pages (current_page tornerà a 0 per default)
        self.writedata.remove_seals_page(self.chat_id, self.user_id)
        medallium_message_id = str(int(self.message_id) + 1)   # message_id del messaggio del bot (risposta al comando)
        self.writedata.add_seals_page(medallium_message_id, self.chat_id, self.user_id)

        # Render pagina 0 (usando la stessa logica che useranno i callbacks)
        text, keyboard = self.render_page(update=update, context=context, page=0)
        seal_photo_path = os.getenv("RESOURCES_OTHER_IMAGES_PATH") +"seals.png"
        await context.bot.send_photo(
            chat_id=self.chat_id,
            photo=open(seal_photo_path, "rb"),
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
