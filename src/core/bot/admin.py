import os
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from config.config import Config
from core.db_manager.getdata import GetData
from core.db_manager.checkdata import CheckData
from core.db_manager.updatedata import UpdateData
from core.db_manager.writedata import WriteData


class AdminCommands:
    def __init__(self):
        self.config = Config()
        self.getData = GetData()
        self.writeData = WriteData()
        self.checkData = CheckData()
        self.updateData = UpdateData()
    
    def _set_context_data(self, update: Update):
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)
        self.user_username = update.effective_user.username
        self.language = self.getData.get_language(self.chat_id)
    
    # Check per vedere se user_id e' in admins.yml
    def _is_admin(self, user_id: str) -> bool:
            admin_list = self.config.get_admins()
            if user_id in admin_list:
                return True
            return False
    
    # Scrive nel file admin_actions.log un record con data, chat, admin e azione eseguita.   
    def _log_admin_action(self, chat_id: str, user_id: str, action: str):
        chat_fullname = self.getData.get_chat_info(chat_id)["chat_fullname"]
        user_fullname = self.getData.get_user_info(user_id)["user_fullname"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = (
            f"[{timestamp}]\n"
            f"Chat: {self.chat_id} ({chat_fullname})\n"
            f"Admin: {self.user_id} ({user_fullname})\n"
            f"Azione: {action}\n\n"
            f"-----------------------------------------\n\n"
        )
        log_path = os.getenv("LOG_PATH")
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_line)

# ------------------------------- #

    async def updatekai(self, update: Update, context: CallbackContext):
        self._set_context_data(update)
        if not self._is_admin(self.user_id):
            await update.message.reply_text("🚫 Non sei autorizzato.", do_quote=True)
            return  
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /updatekai @username amount", do_quote=True)
            return

        try:
            username = context.args[0].lstrip("@")
            kai_amount = int(context.args[1])
            recipient_id = self.getData.get_user_id_from_username(username)
            if not recipient_id:
                await update.message.reply_text("❌ Utente non trovato.", do_quote=True)
                return
            
            # Check record items destinatario
            user_has_items_record = self.checkData.check_user_has_items(recipient_id, self.chat_id)
            if not user_has_items_record:
                self.writeData.add_items(recipient_id, self.chat_id, 0)
            
            # Aggiungi Kai
            self.updateData.update_kai(recipient_id, self.chat_id, kai_amount)
        except Exception:
            print(Exception)
        
        # Comunica in chat e LOGGA l'azione
        action = f"Numero Kai Variato -> {kai_amount} Kai a @{username}"
        self._log_admin_action(chat_id=self.chat_id,
                               user_id=self.user_id,
                               action=action)
        await update.message.reply_text(
            f"✅ Update Kai di: {kai_amount} Kai a @{username}", 
            parse_mode=ParseMode.HTML
        )

# ------------------------------- #

    async def addyokai(self, update: Update, context: CallbackContext):
        self._set_context_data(update)
        if not self._is_admin(self.user_id):
            await update.message.reply_text("🚫 Non sei autorizzato.", do_quote=True)
            return
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /addyokai @username NomeYokai", do_quote=True)
            return

        try:
            username = context.args[0].lstrip("@")
            yokai_name = " ".join(context.args[1:]).lower()  # prende tutto il resto come nome
            recipient_id = self.getData.get_user_id_from_username(username)
            if not recipient_id:
                await update.message.reply_text("❌ Utente non trovato.", do_quote=True)
                return

            # Recupera yokai_id dal nome
            yokai_id = self.getData.get_yokai_id_from_name(yokai_name)
            if not yokai_id:
                await update.message.reply_text("❌ Yo-kai non trovato.", do_quote=True)
                return
            
            # Aggiungi lo yokai al destinatario
            self.writeData.add_yokai_to_user(recipient_id, self.chat_id, yokai_id)

        except Exception:
            return

        # Comunica in chat e LOGGA l'azione
        action = f"Yokai Aggiunto -> {yokai_name} (id {yokai_id}) a @{username}"
        self._log_admin_action(chat_id=self.chat_id,
                               user_id=self.user_id,
                               action=action)
        await update.message.reply_text(
            f"✅ Aggiunto Yo-kai <b>{yokai_name.capitalize()}</b> a @{username}", 
            parse_mode=ParseMode.HTML
        )  

# ------------------------------- #

    async def delyokai(self, update: Update, context: CallbackContext):
        self._set_context_data(update)
        if not self._is_admin(self.user_id):
            await update.message.reply_text("🚫 Non sei autorizzato.", do_quote=True)
            return
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /delyokai @username NomeYokai", do_quote=True)
            return

        try:
            username = context.args[0].lstrip("@")
            yokai_name = " ".join(context.args[1:]).lower()  # prende tutto il resto come nome
            recipient_id = self.getData.get_user_id_from_username(username)
            if not recipient_id:
                await update.message.reply_text("❌ Utente non trovato.", do_quote=True)
                return

            # Recupera yokai_id dal nome
            yokai_id = self.getData.get_yokai_id_from_name(yokai_name)
            if not yokai_id:
                await update.message.reply_text("❌ Yo-kai non trovato.", do_quote=True)
                return
            
            # Controlla se lo yokai e' posseduto dal destinatario
            owned_yokai_ids = self.getData.get_yokai_ids_collected(recipient_id, self.chat_id)
            if yokai_id not in owned_yokai_ids: 
                await update.message.reply_text("❌ Il destinatario non possiede lo yokai.", do_quote=True)
                return

            # Rimuovi lo yokai al destinatario
            self.writeData.remove_yokai_from_user(recipient_id, self.chat_id, yokai_id)

        except Exception:
            return

        # Comunica in chat e LOGGA l'azione
        action = f"Yokai Rimosso -> {yokai_name} (id {yokai_id}) a @{username}"
        self._log_admin_action(chat_id=self.chat_id,
                               user_id=self.user_id,
                               action=action)
        await update.message.reply_text(
            f"✅ Rimosso Yo-kai <b>{yokai_name.capitalize()}</b> a @{username}", 
            parse_mode=ParseMode.HTML
        )  

# ------------------------------- #

    async def annuncia(self, update: Update, context: CallbackContext):
        # Imposta dati del contesto
        self._set_context_data(update)
        # Controllo admin
        if not self._is_admin(self.user_id):
            await update.message.reply_text("🚫 Non sei autorizzato.", do_quote=True)
            return

        # Deve essere risposta a un messaggio
        if not update.message.reply_to_message:
            await update.message.reply_text("Usa /annuncia come risposta al messaggio da inviare!", do_quote=True)
            return

        # Messaggio da inviare e invio a tutti gli utenti
        await update.message.reply_text(
            text="📢 Invio a tutti gli utenti in corso...\nPotrebbe richiedere qualche secondo.",
            parse_mode=ParseMode.HTML
        )

        msg_to_send = update.message.reply_to_message
        text_to_send = msg_to_send.text_html or msg_to_send.text or ""
        users = self.getData.get_all_users()
        sent_count = 0
        failed_count = 0
        result_text = f"✅ Annuncio inviato a:\n"
        for user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=text_to_send,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                sent_count += 1
                result_text += f"{sent_count}) @{self.getData.get_user_info(user_id)['user_username']}\n"
            except Exception as e:
                # Ignora utenti che hanno bloccato il bot
                failed_count += 1
                
        # Risposta in chat admin
        await update.message.reply_text(
            text=result_text + f"\n\n❌ Falliti: {failed_count}",
            parse_mode=ParseMode.HTML
        )
