import os
from dotenv import load_dotenv
from core.bot.setup import BotManager

# forza la cartella corrente a src/
os.chdir(os.path.dirname(__file__))

# Carica le variabili d'ambiente dal file .env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Ottieni il token dal file .env
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Questo è il punto di ingresso principale per l'applicazione del bot.
def main():
    bot = BotManager(BOT_TOKEN) 
    print("Bot is online!")
    bot.run()

if __name__ == "__main__":
    main()
