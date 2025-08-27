import os
from dotenv import load_dotenv
from core.bot.setup import BotManager

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Ottieni il token dal file .env
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Questo è il punto di ingresso principale per l'applicazione del bot.
def main():
    bot = BotManager(BOT_TOKEN) 
    print("Bot is online!")
    bot.run()

if __name__ == "__main__":
    main()
