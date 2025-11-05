# pylint: disable=line-too-long

import config
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import datetime

bot = config.bot


def prepare_games_list_keyboard(games_json: dict) -> tuple[ReplyKeyboardMarkup, dict]:
    keyboard = ReplyKeyboardMarkup()
    date_format: str = "%d.%m.%Y %H:%M"
    count_games = 0
    events_data: dict = dict()
    for el in games_json:
        game_date: str = el.get("Когда")
        game_date: datetime.datetime = datetime.datetime.strptime(game_date, date_format)
        if game_date >= datetime.datetime.today():
            events_data[f"{el.get('Что')} | {el.get('Когда')}"] = {
                "Что": el.get("Что"),
                "Когда": el.get("Когда"),
                "Где": el.get("Где"),
                "Состав": el.get("Состав")
            }
            if count_games % 2 == 0:
                prev_game = KeyboardButton(f"{el.get('Что')} | {el.get('Когда')}")
            else:
                keyboard.row(prev_game, KeyboardButton(f"{el.get('Что')} | {el.get('Когда')}"))
            count_games += 1
    keyboard.row(KeyboardButton("Главное меню"))
    return keyboard, events_data
