import os
from PIL import Image
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData

class FlexCommand:
    def __init__(self):
        self.config = Config()
        self.getData = GetData()

    # Inizializza variabili di contesto
    def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)
        self.user_username = update.effective_user.username
        self.language = self.getData.get_language(self.chat_id)
        # Recupera il testo dopo il comando (/flex o /flex@botusername)
        message_text = update.message.text or ""
        parts = message_text.split(maxsplit=1)
        if len(parts) > 1:
            self.message_text = parts[1].strip()
        else:
            self.message_text = ""


    # Restituisce il fattore di scala associato a un determinato Yo-kai.
    def _get_scale(self, yokai_id: str) -> float:
        DEFAULT_SCALE = 0.75
        scale_map = {
            0.3: {"-1", "-2", "-6", "321", "444"},
            0.1: {"-12"},
            0.4: {"241", "271", "285", "530", "594", "595", "596", "597", "598", "643", "745", "746", "752"},
            1.5: {"-4", "100", "445", "494", "518", "750", "751"},
            1.75: {"238", "239"},
            3.0: {"434", "435", "436", "437"},
        }
        for scale_value, ids in scale_map.items():
            if yokai_id in ids:
                return scale_value
        return DEFAULT_SCALE

    def _generate_flex_image(self, yokai_id: str) -> str:
        '''
            Ritorna il path dell'immagine generata, oltre a generarla nella
            directory in questione. Poi l'immagine sara eliminata (dunque e' temp)
        '''
        yokai_image_path = os.getenv("RESOURCES_YOKAI_IMAGES_PATH") + f"{yokai_id}.png"
        stage_photo_path = os.getenv("RESOURCES_OTHER_IMAGES_PATH") + "stage.png"

        # Carica le due immagini: sfondo e yokai (overlay) e prendi le misure
        background = Image.open(stage_photo_path).convert("RGBA")
        overlay = Image.open(yokai_image_path).convert("RGBA")
        bg_width, bg_height = background.size
        overlay_width, overlay_height = overlay.size

        # Correggi le misure per gli yokai della tupla 
        scale = self._get_scale(yokai_id)
        new_overlay_width, new_overlay_height = (int(overlay_width * scale), int(overlay_height * scale))
        overlay = overlay.resize((new_overlay_width, new_overlay_height), Image.LANCZOS)
        
        # Calcola posizione centrata
        x = (bg_width - new_overlay_width) // 2
        y = (bg_height - new_overlay_height) // 2

        # Crea immagine e ritorna il path (questa directory stessa)
        result = background.copy()
        result.paste(overlay, (x, y), overlay)
        output_image = "flex_image.png"  # questa foto sara' temporanea
        result.save(output_image, "PNG")  
        return output_image  
        

    async def flex(self, update: Update, context: CallbackContext):
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

        # Se non è stato scritto niente dopo /flex (cioe message_text == "")
        if not self.message_text:
            await update.message.reply_text(
                text=self.config.get_text('flexguide', self.language),
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
        
        # Verifica se l'utente ha lo yokai da flexare
        owned_yokai_ids = self.getData.get_yokai_ids_collected(self.user_id, self.chat_id)
        if yokai_id not in owned_yokai_ids:
            await update.message.reply_text(
                text=self.config.get_text("yokainotgot", self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Genera il messaggio di flex
        yokai_rank = self.getData.get_yokai_info(yokai_id)["rank"]
        if yokai_rank:
            yokai_rank = yokai_rank.capitalize()
        yokai_ids = self.getData.get_yokai_ids_collected(self.user_id, self.chat_id)
        duplicates = yokai_ids.count(yokai_id)
        how_many_owners_in_group = self.getData.get_yokai_owners_count_in_group(yokai_id, self.chat_id)
        global_yokai_befriended_count = self.getData.get_global_yokai_count(yokai_id)
        
        if int(yokai_id) > 0:   # Se e' uno yokai normale
            text = (
                f"@{self.user_username} {self.config.get_text("flexmessage", self.language)[0]} <b>{self.message_text.capitalize()}</b>\n\n"
                f"{self.config.get_text("flexmessage", self.language)[1]} <b>{yokai_id}</b>\n"
                f"{self.config.get_text("flexmessage", self.language)[2]} <b>{yokai_rank}</b>\n"
                f"{self.config.get_text("flexmessage", self.language)[3]} <b>{duplicates}</b>\n"
                f"{self.config.get_text("flexmessage", self.language)[4]} <b>{how_many_owners_in_group}</b>\n"
                f"{self.config.get_text("flexmessage", self.language)[5]} <b>{global_yokai_befriended_count}</b>"
            )
        else:   # Se e' uno yokai speciale
            text = (
                f"@{self.user_username} {self.config.get_text("flexmessage", self.language)[0]} <b>{self.message_text.capitalize()}</b>\n\n"
                f"{self.config.get_text("flexmessage", self.language)[1]} <b>Special {-yokai_id}</b>\n\n"
                f"{self.config.get_text("flexmessage", self.language)[6]}"
            )
            
        yokai_id = self.getData.get_yokai_id_from_name(self.message_text)
        temp_file_path = self._generate_flex_image(yokai_id)
        await context.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=open(temp_file_path, "rb"),
                    caption=text,
                    parse_mode=ParseMode.HTML
                )
        os.remove(temp_file_path)   # Rimuovi la foto flex che era temporanea
