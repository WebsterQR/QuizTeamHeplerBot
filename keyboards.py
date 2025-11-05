# pylint: disable=line-too-long

from telebot.types import ReplyKeyboardMarkup, KeyboardButton




class MainMenu:
    keyboard = ReplyKeyboardMarkup()
    games_table = KeyboardButton("🗂 Таблица игр в GoogleSheets")
    games_calendar = KeyboardButton("📇 Список ближайших игр")
    keyboard.row(games_table)
    keyboard.row(games_calendar)


