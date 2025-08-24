from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config.config import Config
from core.bot.callbacks_handler import CallbackHandler
from core.bot.message_handlers import MessHandlers
from core.bot.admin import AdminCommands
from core.bot.command_handlers import basic, friend, medallium, inventory, leaderboard, release, ykgift

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters


class BotManager:
    def __init__(self):
        TOKEN = Config().get_botConfig("token")
        self.application = ApplicationBuilder().token(TOKEN).build()

    def _setup_handlers(self):
        admin_cmds = AdminCommands()
        basic_cmds = basic.BasicCommands()
        friend_cmd = friend.FriendCommand()
        medallium_cmd = medallium.MedalliumCommand()
        inventory_cmd = inventory.InventoryCommand()
        leaderboard_cmd = leaderboard.LeaderboardCommand()
        release_cmd = release.ReleaseCommand()
        ykgift_cmd = ykgift.YkgiftCommand()  
        
        mess_handler = MessHandlers()
        callbacks_handler = CallbackHandler()

        # Comandi base
        self.application.add_handler(CommandHandler("start", basic_cmds.start))
        self.application.add_handler(CommandHandler(("help", "commands", "comandi"), basic_cmds.help))
        self.application.add_handler(CommandHandler(("contact", "contatta"), basic_cmds.contact))
        self.application.add_handler(CommandHandler(("settings", "options", "impostazioni", "opzioni"), basic_cmds.settings))
        self.application.add_handler(CommandHandler(("crankakai", "slotkai"), basic_cmds.crankakai))

        # Comandi avanzati
        self.application.add_handler(CommandHandler("friend", friend_cmd.friend))
        self.application.add_handler(CommandHandler(("medallium", "medaglium"), medallium_cmd.medallium))
        self.application.add_handler(CommandHandler("ykgift", ykgift_cmd.ykgift))
        self.application.add_handler(CommandHandler(("release", "rilascia"), release_cmd.release))
        self.application.add_handler(CommandHandler(("inventory", "inventario"), inventory_cmd.inventory))
        self.application.add_handler(CommandHandler(("leaderboard", "classifica"), leaderboard_cmd.leaderboard))

        # Comandi per gli operatori speciali (ykwi)
        self.application.add_handler(CommandHandler("addkai", admin_cmds.addkai))
        self.application.add_handler(CommandHandler("addyokai", admin_cmds.addyokai))

        # Callback buttons
        self.application.add_handler(CallbackQueryHandler(callbacks_handler.handle_callbacks))

        # Messaggi gruppo e nuovi utenti
        self.application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, mess_handler.handle_new_members))
        self.application.add_handler(MessageHandler(filters.ChatType.GROUPS, mess_handler.handle_messages))

    def run(self):
        self._setup_handlers()
        self.application.run_polling(drop_pending_updates=True)
