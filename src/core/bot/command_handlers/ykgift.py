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
        
        # Verifica se lo Yo-Kai da regalare e' speciale o leggendario (non puo' essere regalato)
        if int(yokai_id) < 0 or yokai_id in self.getData.get_legendary_yokai_ids():
            await update.message.reply_text(
                text=self.config.get_text("cantgift", self.language),
                parse_mode=ParseMode.HTML,
                do_quote=True
            )
            return
        
        """
            Controllo validità regalo Yokai legato ai sigilli.
            Regola:
            - Se il destinatario possiede già lo Yokai → regalo consentito.
            - Se NON lo possiede:
                → il regalo è consentito solo se TUTTI i sigilli che richiedono
                questo Yokai sono già stati completati.
            - Se esiste almeno un sigillo incompleto che lo richiede → blocco.
        """
        
        seals_yokai_ids = self.getData.get_every_requirements_seals_ids()
        recipient_yokai_ids = self.getData.get_yokai_ids_collected(recipient_id, self.chat_id)
        legendary_yokai_ids = self.getData.get_legendary_yokai_ids()

        can_be_gifted = False
        if yokai_id not in seals_yokai_ids:     #  Se non è un requisito di alcun sigillo, nessun problema
            can_be_gifted = True
        if yokai_id in recipient_yokai_ids:     #  Se il destinatario lo possiede già, va bene (una copia vale per tutti)
            can_be_gifted = True

        if not can_be_gifted:
            # A questo punto:
            # - è un requisito di almeno un sigillo
            # - il destinatario NON lo possiede
            # → dobbiamo verificare se esiste un sigillo incompleto che lo richiede
            for legendary_id in legendary_yokai_ids:
                requirements_ids = self.getData.get_legendary_requirements_ids_from_yokaiID(legendary_id)
                # Se questo leggendario richiede lo yokai
                if yokai_id in requirements_ids:
                    # Se il leggendario NON è ancora posseduto → sigillo incompleto
                    if legendary_id not in recipient_yokai_ids:
                        await update.message.reply_text(
                            text=self.config.get_text("cantgiftseal", self.language),
                            parse_mode=ParseMode.HTML,
                            do_quote=True
                        )
                        return

        ''' --------------------------------------------------------------- '''

        # Dopo tutte le verifiche, effettua lo scambio e comunica l'avvenuto regalo
        self.writeData.remove_yokai_from_user(self.user_id, self.chat_id, int(yokai_id))
        self.writeData.add_yokai_to_user(recipient_id, self.chat_id, int(yokai_id))

        await update.message.reply_text(
            f"<i>Yo-Kai: <b>{yokai_name.capitalize()}</b> {self.config.get_text('ykgiftdone', self.language)}</i>\n"
            f"@{self.user_username} ---> @{recipient_username}\n",
            parse_mode=ParseMode.HTML, 
            do_quote=False
        )
