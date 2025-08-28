import yaml
import os

class Config:
    def __init__(self):
        # Percorsi file YAML
        self.bot_path = os.getenv("CONFIG_BOT_PATH")
        self.texts_path = os.getenv("CONFIG_TEXTS_PATH")
        self.urls_path = os.getenv("CONFIG_URLS_PATH")
        self.admin_path = os.getenv("CONFIG_ADMINS_PATH")

        # Carica i contenuti YAML
        self.bot = self._load_yaml(self.bot_path)
        self.texts = self._load_yaml(self.texts_path)
        self.urls = self._load_yaml(self.urls_path)
        self.admins = self._load_yaml(self.admin_path)

    def _load_yaml(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


    # Metodi per ottenere configurazioni specifiche in 
    # bot.yml | texts.yml | urls.yml | admins.yml

    def get_botConfig(self, key: str):
        return self.bot[key]

    def get_text(self, key: str, lang_key: str):
        return self.texts[key][lang_key]
    
    def get_url(self, key: str):
        return self.urls[key]
    
    def get_admins(self):
        return self.admins


# Esempio d'uso (se vuoi testare)
if __name__ == "__main__":
    conf = Config()
    print(conf.get_aBotConfig("token"))         
    print(conf.get_aText("startprivate"))    
    