from core.bot.setup import BotManager

# This is the main entry point for the bot application.
def main():
    bot = BotManager()  
    print("Bot is online!")
    bot.run()

if __name__ == "__main__":
    main()
