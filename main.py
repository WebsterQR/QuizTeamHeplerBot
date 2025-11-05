from time import sleep

import config
import constants
import helpers
import keyboards
import requests

bot = config.bot


@bot.message_handler(commands=['help', 'start'])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Выберите функцию",
        reply_markup=keyboards.MainMenu.keyboard
    )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Главное меню":
        bot.send_message(
            chat_id=message.chat.id,
            text="Выберите функцию",
            reply_markup=keyboards.MainMenu.keyboard
        )
    if message.text == "🗂 Таблица игр в GoogleSheets":
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Если нужна таблица в гугл таблицах, то вот ссылка {constants.Links.team_table}",
            reply_markup=keyboards.MainMenu.keyboard
        )
    elif message.text == "📇 Список ближайших игр":
        all_games_response = requests.get(config.TABLE_API.token)
        all_games_response.encoding = "utf-8"
        all_games_data = all_games_response.json()
        games_keyboard, _ = helpers.prepare_games_list_keyboard(all_games_data)
        bot.send_message(
            chat_id=message.chat.id,
            text="Вот список ближайших игр",
            reply_markup=games_keyboard
        )
    else:
        all_games_response = requests.get(config.TABLE_API.token)
        all_games_response.encoding = "utf-8"
        all_games_data = all_games_response.json()
        games_keyboard, events_list = helpers.prepare_games_list_keyboard(all_games_data)
        events_names = events_list.keys()
        if message.text in events_names:
            current_event = events_list.get(message.text)
            formatted_composition = '\n\t'.join(current_event.get("Состав").split("\n"))
            msg = (
                f"<b><u>Инфо об игре</u></b>:\n"
                f"<b>Тема:</b> {current_event.get('Что')}\n"
                f"<b>Локация:</b> {current_event.get('Где')}\n"
                f"<b>Дата и время:</b> {current_event.get('Когда')}\n"
                f"<b>Состав:</b>\n"
                f"\t{formatted_composition}"
            )
            bot.send_message(
                chat_id=message.chat.id,
                text=msg,
                reply_markup=keyboards.MainMenu.keyboard,
                parse_mode="HTML"
            )


while True:
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(10)
