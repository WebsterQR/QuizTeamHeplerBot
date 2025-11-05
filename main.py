from time import sleep

import config
import constants
import helpers
import keyboards

bot = config.bot


@bot.message_handler(commands=['help', 'start'])
def start(message):
    chat_type = message.chat.type
    if chat_type == "private":
        bot.send_message(
            chat_id=message.chat.id,
            text="Выберите функцию",
            reply_markup=keyboards.MainMenu.keyboard
        )
    else:
        bot.reply_to(
            message=message,
            text="Я знаю эту команду, но отвечаю на нее только в личке. Чтобы не спамить в чате :)"
        )


@bot.message_handler(commands=["calendar"])
def echo_games(message):
    _, events = helpers.get_games_schedule_data()
    prepared_answer = "<b>Вот список ближайших игр:</b> \n"
    for event in events:
        prepared_answer += f"* {event}\n"
    bot.reply_to(
        message=message,
        text=prepared_answer,
        parse_mode="HTML"
    )


@bot.message_handler(commands=["table"])
def echo_table(message):
    prepared_answer = f"Тебе нужна ссылка на таблицу?\n <a href='{constants.Links.team_table}'>Держи!</a>"
    bot.reply_to(
        message=message,
        text=prepared_answer,
        parse_mode="HTML"
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
        games_keyboard, _ = helpers.get_games_schedule_data()
        bot.send_message(
            chat_id=message.chat.id,
            text="Вот список ближайших игр",
            reply_markup=games_keyboard
        )
    else:
        games_keyboard, events_list = helpers.get_games_schedule_data()
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
