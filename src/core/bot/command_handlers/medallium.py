from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.writedata import WriteData
from core.db_manager.updatedata import UpdateData
from core.bot.keyboards import Keyboards


class MedalliumCommand:
    def __init__(self):
        self.getdata = GetData()
        self.writedata = WriteData()
        self.updatedata = UpdateData()
        self.config = Config()
        self.keyboards = Keyboards()

    #   Funzione di inizializzazione contesto
    def _set_context_data(self, update: Update, context: CallbackContext):
        if update.message:  # dati presi inviando il comando /medallium
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


    # ------------------------------
    #   Helpers di paging (riutilizzabili da callbacks)
    # ------------------------------

    # --- Costruisce la pagina delle statistiche
    def _build_stats_page(self, update: Update, context: CallbackContext, 
                          yokai_ids: list[str]): 
        
        self._set_context_data(update, context)  
        NYOKAI = self.config.get_botConfig("nyokai")
        number_yokai_friended = len(yokai_ids)
        last_yokai_friended = self.getdata.get_yokai_name_from_id(str(yokai_ids[-1]), self.language).capitalize()
        duplicates = sum(yokai_ids.count(id_) - 1 for id_ in set(yokai_ids))
        medallium_completion = round(len(set(yokai_ids)) * 100 / NYOKAI, 1)

        message_text = (
            f"@{self.user_username} {self.config.get_text('showmedallium', self.language)[0]}"
            f"{self.config.get_text('showmedallium', self.language)[1]} {number_yokai_friended}"
            f"{self.config.get_text('showmedallium', self.language)[2]} {last_yokai_friended}"
            f"{self.config.get_text('showmedallium', self.language)[3]} {duplicates}"
            f"{self.config.get_text('showmedallium', self.language)[4]} {medallium_completion}%"
        )
        keyboard = self.keyboards.get_keyboard("right_kb", self.language)
        return message_text, keyboard


    # --- Costruisce le pagina del Medallium, ordinata correttamente
    def _build_yokai_page(self, update: Update, context: CallbackContext, 
                      yokai_ids: list[str], page: int):
        self._set_context_data(update, context)

        # 1) Converti in interi la yokai_ids e crea dizionario {yokai_id: quantita'}
        yokai_ids_int = [int(y_id) for y_id in yokai_ids]
        yokai_count = {yid: yokai_ids_int.count(yid) for yid in set(yokai_ids_int)}
        
        # 2) Suddivisione speciali e normali
        specials = [y for y in yokai_count if y < 0]
        normals = [y for y in yokai_count if y > 0]

        # 3) Gestisci ordinamento in base a sort_mode:
        #     - "id"          → speciali prima (ID decrescente), poi normali (ID crescente)
        #     - "alphabetic"  → speciali prima (ordinati per nome), poi normali (ordinati per nome)
        #     In entrambi i casi gli speciali sono sempre messi davanti ai normali
        sort_mode = self.getdata.get_medallium_pages_data(self.message_id, self.chat_id)["sort_mode"]
    
        if sort_mode == "id":   # Ordine classico per ID
            specials_sorted = sorted(specials, reverse=True)   # speciali: ID decrescente
            normals_sorted = sorted(normals)                   # normali: ID crescente
        elif sort_mode == "alphabetical":
            # Dalle liste specials e normals crei delle parallele dove al posto degli ID hai i nomi degli yokai
            specials_names = [self.getdata.get_yokai_name_from_id(str(y), self.language).lower() for y in specials]
            normals_names = [self.getdata.get_yokai_name_from_id(str(y), self.language).lower() for y in normals]
            # Genera le liste di ID degli yokai ordinate alfabeticamente in base al loro nome
            # - specials_sorted contiene gli ID speciali
            # - normals_sorted contiene gli ID normali
            specials_sorted = [y for _, y in sorted(zip(specials_names, specials))]
            normals_sorted = [y for _, y in sorted(zip(normals_names, normals))]

        # 5) Suddivisione in pagine sulla base di yokai_list totale e PER_PAGE costante
        yokai_list = specials_sorted + normals_sorted
        PER_PAGE = self.config.get_botConfig("yokai_perpage_in_medallium")
        pages = [tuple(yokai_list[i:i + PER_PAGE]) for i in range(0, len(yokai_list), PER_PAGE)]

        # 6) Genera testo della pagina 
        text = f"📖 @{self.user_username}<i>'s Medallium</i>\n<b>Page N. {page})</b>\n\n"
        current_page_tuple = pages[page - 1]
        for yokai_id in current_page_tuple:
            yokai_name = self.getdata.get_yokai_name_from_id(str(yokai_id), self.language).capitalize()     
            dup = yokai_count[yokai_id]
            dup_text = f"[x{dup}]" if dup > 1 else ""
            if yokai_id < 0:
                text += f"⭐️ <b>Special {-yokai_id}</b>.\n<i>Yo-Kai</i>:  {yokai_name}    <b>{dup_text}</b>\n\n"
            else:
                text += f"🆔: <b>{yokai_id}</b>.\n<i>Yo-Kai</i>:  {yokai_name}    <b>{dup_text}</b>\n\n"

        # 7) Crea la tastiera di navigazione in base alla pagina attuale e al sort_mode
        # other_sort_mode e' usata per sapere quale sort_mode NON e' attivo (per il bottone di switch)
        other_sort_mode = "alphabetical" if sort_mode == "id" else "id"

        if page == 0:   # pagina statistiche
            keyboard = self.keyboards.get_keyboard("right_kb", self.language)
        elif page == len(pages):    # ultima pagina 
            keyboard = self.keyboards.get_keyboard(f"left_sort_{other_sort_mode}_kb", self.language)
        else:   # pagine intermedie 
            keyboard = self.keyboards.get_keyboard(f"rightleft_sort_{other_sort_mode}_kb", self.language)

        return text, keyboard


    # ------------------------------------------
    #   Comando /medallium (render_page e' utilizzata anche in callbacks)
    # ------------------------------------------

    # Decidi quale pagina mostrare in base al numero di pagina
    def render_page(self, update: Update, context: CallbackContext, yokai_ids: list[str], page: int):
        """
        - page == 0  -> stats
        - page >= 1  -> pagine yokai
        """
        if page == 0:
            return self._build_stats_page(update=update, context=context, yokai_ids=yokai_ids)
        elif page > 0:
            return self._build_yokai_page(update=update, context=context, yokai_ids=yokai_ids, page=page)

    async def medallium(self, update: Update, context: CallbackContext):
        # Non disponibile in privato
        if update.message.chat.type == "private":
            await update.message.reply_text(
                text=self.config.get_text("onlyingroups", "en"),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return
        self._set_context_data(update, context)

        # Yokai posseduti
        yokai_ids = self.getdata.get_yokai_ids_collected(self.user_id, self.chat_id)
        # Caso medallium vuoto
        if not yokai_ids:
            await update.message.reply_text(
                self.config.get_text("emptymedallium", self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return

        # Elimina il vecchio messaggio del medallium, se esiste
        old_message_id = self.getdata.get_message_id_from_medallium_pages(self.chat_id, self.user_id)
        if old_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=self.chat_id,
                    message_id=old_message_id
                )
            except Exception:   # Magari il messaggio era già stato eliminato manualmente
                pass

        # Elimina e reinserisci il corretto record in medallium_pages (current_page tornerà a 0 per default)
        self.writedata.remove_medallium_page(self.chat_id, self.user_id)
        medallium_message_id = str(int(self.message_id) + 1)   # message_id del messaggio del bot (risposta al comando)
        self.writedata.add_medallium_page(medallium_message_id, self.chat_id, self.user_id)

        # Render pagina 0 (usando la stessa logica che useranno i callbacks)
        text, keyboard = self.render_page(update=update, context=context, yokai_ids=yokai_ids, page=0)
        await update.message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            do_quote=False
        )
