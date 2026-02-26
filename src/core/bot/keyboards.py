from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.config import Config

class Keyboards:
    def __init__(self):
        self.config = Config()
    
    def _get_button(self, button_key: str, lang_key: str) -> InlineKeyboardButton:
        # Bottoni con testo fisso (url)
        url_buttons = {
            "addbot_button": InlineKeyboardButton(text="Add Bot ➕", url=self.config.get_url("addbot_url")),
            "guide_button": InlineKeyboardButton(text="Yo-kai database 📜", url=self.config.get_url("guide_url")),
            "credits_button": InlineKeyboardButton(text="Credits ⭐", url=self.config.get_url("credits_url")),
            "YoKaiMedalsSupport_button": InlineKeyboardButton(text="Support 🆘", url=self.config.get_url("support_url")),
            "YoKaiMedalsChannel_button": InlineKeyboardButton(text="Channel 📣", url=self.config.get_url("channel_url")),
        }
        if button_key in url_buttons:
            return url_buttons[button_key]
        
        # Bottoni con testo da texts.yml supponendo che sia un dict. es: { "spawnrangefast_button": ["Fast", "Veloce"], ... }
        buttons = {
            # spawnrange buttons
            "spawnrangefast_button": InlineKeyboardButton(text=self.config.get_text("spawnrangefast_button",lang_key), callback_data="fast", api_kwargs={"style": "success"}),
            "spawnrangemedium_button": InlineKeyboardButton(text=self.config.get_text("spawnrangemedium_button", lang_key), callback_data="medium", api_kwargs={"style": "primary"}),
            "spawnrangeslow_button": InlineKeyboardButton(text=self.config.get_text("spawnrangeslow_button", lang_key), callback_data="slow", api_kwargs={"style": "danger"}),

            # language buttons
            "eng_button": InlineKeyboardButton(text=self.config.get_text("eng_button", lang_key), callback_data="en"),
            "ita_button": InlineKeyboardButton(text=self.config.get_text("ita_button", lang_key), callback_data="it"),

            # medallium page buttons
            "medallium_right_button": InlineKeyboardButton(text=self.config.get_text("right_button", lang_key), callback_data="right_medallium"),
            "medallium_left_button": InlineKeyboardButton(text=self.config.get_text("left_button", lang_key), callback_data="left_medallium"),
            "sort_button_id": InlineKeyboardButton(text=self.config.get_text("sort_button_id", lang_key), callback_data="sort_id"),
            "sort_button_alphabetical": InlineKeyboardButton(text=self.config.get_text("sort_button_alphabetical", lang_key), callback_data="sort_alphabetical"),

            # seals page buttons
            "seals_right_button": InlineKeyboardButton(text=self.config.get_text("right_button", lang_key), callback_data="right_seals"),
            "seals_left_button": InlineKeyboardButton(text=self.config.get_text("left_button", lang_key), callback_data="left_seals"),
            "checkseal_button": InlineKeyboardButton(text=self.config.get_text("checkseal_button", lang_key), callback_data="check_seal"),

            # coins buttons
            "redcoin_button": InlineKeyboardButton(text=self.config.get_text("redcoin_button", lang_key), callback_data="red"),
            "yellowcoin_button": InlineKeyboardButton(text=self.config.get_text("yellowcoin_button", lang_key), callback_data="yellow"),
            "orangecoin_button": InlineKeyboardButton(text=self.config.get_text("orangecoin_button", lang_key), callback_data="orange"),
            "pinkcoin_button": InlineKeyboardButton(text=self.config.get_text("pinkcoin_button", lang_key), callback_data="pink"),
            "greencoin_button": InlineKeyboardButton(text=self.config.get_text("greencoin_button", lang_key), callback_data="green"),
            "bluecoin_button": InlineKeyboardButton(text=self.config.get_text("bluecoin_button", lang_key), callback_data="blue"),
            "purplecoin_button": InlineKeyboardButton(text=self.config.get_text("purplecoin_button", lang_key), callback_data="purple"),
            "skybluecoin_button": InlineKeyboardButton(text=self.config.get_text("skybluecoin_button", lang_key), callback_data="skyblue"),
            "onestarcoin_button": InlineKeyboardButton(text=self.config.get_text("onestarcoin_button", lang_key), callback_data="one_star"),
            "fivestarcoin_button": InlineKeyboardButton(text=self.config.get_text("fivestarcoin_button", lang_key), callback_data="five_stars"),
            "specialcoin_button": InlineKeyboardButton(text=self.config.get_text("specialcoin_button", lang_key), callback_data="special"),

            # settings buttons
            "spawnranges_button": InlineKeyboardButton(text=self.config.get_text("spawnranges_button", lang_key), callback_data="open_spawnranges_setting"),
            "languages_button": InlineKeyboardButton(text=self.config.get_text("languages_button", lang_key), callback_data="open_language_setting"),
            "contacts_button": InlineKeyboardButton(text=self.config.get_text("contacts_button", lang_key), callback_data="open_contacts_setting"),
            "closesettings_button": InlineKeyboardButton(text=self.config.get_text("closesettings_button", lang_key), callback_data="close_settings"),
            "backtosettings_button": InlineKeyboardButton(text=self.config.get_text("backtosettings_button", lang_key), callback_data="back_to_settings"),
        }
        return buttons[button_key]


    def get_keyboard(self, keyboard_name: str, lang_key: str) -> InlineKeyboardMarkup:
        kb = {
            "start_kb": InlineKeyboardMarkup([
                [self._get_button("addbot_button", lang_key)],
                [self._get_button("guide_button", lang_key), self._get_button("credits_button", lang_key)],
                [self._get_button("YoKaiMedalsChannel_button", lang_key), self._get_button("YoKaiMedalsSupport_button", lang_key)],
            ]),
            "guide_kb": InlineKeyboardMarkup([[self._get_button("guide_button", lang_key)]]),
            "settings_kb": InlineKeyboardMarkup([
                [self._get_button("languages_button", lang_key), self._get_button("spawnranges_button", lang_key)],
                [self._get_button("contacts_button", lang_key), self._get_button("closesettings_button", lang_key)],
            ]),

            "lang_kb_without_back": InlineKeyboardMarkup([[self._get_button("eng_button", lang_key), self._get_button("ita_button", lang_key)],]),
            "lang_kb": InlineKeyboardMarkup([
                [self._get_button("eng_button", lang_key), self._get_button("ita_button", lang_key)],
                [self._get_button("backtosettings_button", lang_key)],
            ]),

            "contactsettings_kb": InlineKeyboardMarkup([
                [self._get_button("YoKaiMedalsSupport_button", lang_key), self._get_button("credits_button", lang_key)],
                [self._get_button("YoKaiMedalsChannel_button", lang_key), self._get_button("backtosettings_button", lang_key)],
            ]),
            "spawnrange_kb": InlineKeyboardMarkup([
                [self._get_button("spawnrangefast_button", lang_key)],
                [self._get_button("spawnrangemedium_button", lang_key)],
                [self._get_button("spawnrangeslow_button", lang_key)],
                [self._get_button("backtosettings_button", lang_key)],
            ]),
            "contact_kb": InlineKeyboardMarkup([
                [self._get_button("YoKaiMedalsSupport_button", lang_key), self._get_button("credits_button", lang_key)],
                [self._get_button("YoKaiMedalsChannel_button", lang_key)],
            ]),

            "shopcoins_kb": InlineKeyboardMarkup([
                            [self._get_button("redcoin_button", lang_key), self._get_button("yellowcoin_button", lang_key)],
                            [self._get_button("orangecoin_button", lang_key), self._get_button("purplecoin_button", lang_key)],
                            [self._get_button("greencoin_button", lang_key), self._get_button("bluecoin_button", lang_key)],
                            [self._get_button("pinkcoin_button", lang_key), self._get_button("skybluecoin_button", lang_key)],
                            [self._get_button("onestarcoin_button", lang_key), self._get_button("fivestarcoin_button", lang_key)],
                            [self._get_button("specialcoin_button", lang_key)],
                        ]),


            # Medallium navigation keyboards
            # La medallium_right_kb e' unica perche riguarda solo la pagina statistiche, cioe la 0
            "medallium_right_kb": InlineKeyboardMarkup([[self._get_button("medallium_right_button", lang_key)]]),
            
            "rightleft_sort_id_kb": InlineKeyboardMarkup([
                [self._get_button("medallium_left_button", lang_key), self._get_button("medallium_right_button", lang_key)],
                [self._get_button("sort_button_id", lang_key)]
            ]),
            "rightleft_sort_alphabetical_kb": InlineKeyboardMarkup([
                [self._get_button("medallium_left_button", lang_key), self._get_button("medallium_right_button", lang_key)],
                [self._get_button("sort_button_alphabetical", lang_key)]
            ]),
            
            "left_sort_id_kb": InlineKeyboardMarkup([
                [self._get_button("medallium_left_button", lang_key)],
                [self._get_button("sort_button_id", lang_key)]
            ]), 
            "left_sort_alphabetical_kb": InlineKeyboardMarkup([
                [self._get_button("medallium_left_button", lang_key)],
                [self._get_button("sort_button_alphabetical", lang_key)]
            ]),

            # Seals navigation keyboards
            "seals_right_kb": InlineKeyboardMarkup([[self._get_button("seals_right_button", lang_key)]]),

            "seals_left_kb": InlineKeyboardMarkup([
                [self._get_button("checkseal_button", lang_key)],
                [self._get_button("seals_left_button", lang_key)]
            ]),

            "seals_rightleft_kb": InlineKeyboardMarkup([
                [self._get_button("checkseal_button", lang_key)],
                [self._get_button("seals_left_button", lang_key), self._get_button("seals_right_button", lang_key)]
            ]),

        }
        return kb[keyboard_name]
