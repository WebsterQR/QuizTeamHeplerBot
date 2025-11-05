from time import sleep

import config
import constants
import database
import helpers
import keyboards
import requests

# bot = telebot.TeleBot(config.Telegram.TOKEN)
bot = config.bot


@bot.message_handler(commands=['help', 'start'])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Выберите функцию",
        reply_markup=keyboards.NewMainMenu.keyboard
    )

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "Главное меню":
        print("111")
        bot.send_message(
            chat_id=message.chat.id,
            text="Выберите функцию",
            reply_markup=keyboards.NewMainMenu.keyboard
        )
    if message.text == "🗂 Таблица игр в GoogleSheets":
        bot.send_message(
            chat_id=message.chat.id,
            text="Если нужна таблица в гугл таблицах, то вот ссылка <link>",
            reply_markup=keyboards.NewMainMenu.keyboard
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
            print(f"{current_event=}")
            msg = f"<b><u>Инфо об игре</u></b>: \n<b>Тема:</b> {current_event.get("Что")} \n<b>Локация:</b> {current_event.get("Где")} \n<b>Дата и время:</b> {current_event.get("Когда")} \n<b>Состав:</b>\n\t{"\n\t".join(current_event.get("Состав").split("\n"))}"
            bot.send_message(
                chat_id=message.chat.id,
                text=msg,
                reply_markup=keyboards.NewMainMenu.keyboard,
                parse_mode="HTML"
            )
        

@bot.message_handler(commands=['menu'])
def menu(message):
    reply_keyboard = keyboards.MainMenuForAdmins \
        if message.from_user.username in config.ADMIN_USERS else keyboards.MainMenu
    bot.send_message(message.chat.id, text="", reply_markup=reply_keyboard.keyboard)


@bot.message_handler(content_types=["text"])
def parse_text_register(message):  # noqa: C901
    if message.text == "Авторизоваться":
        if not database.check_user_already_exist(message.chat.id):
            first_name = message.from_user.first_name if message.from_user.first_name else ""
            last_name = message.from_user.last_name if message.from_user.last_name else ""
            database.add_user(chat_id=message.chat.id,
                              name=first_name + " " + last_name,
                              login=message.from_user.username)
            answer = constants.TextTemplates.message_after_auth
        else:
            answer = constants.TextTemplates.message_already_auth

        reply_keyboard = keyboards.MainMenuForAdmins \
            if message.from_user.username in config.ADMIN_USERS else keyboards.MainMenu
        bot.send_message(chat_id=message.chat.id, text=answer, reply_markup=reply_keyboard.keyboard)

    if message.text == "Сделать рассылку":
        answer = "Укажи текст который нужно отправить"
        msg = bot.send_message(chat_id=message.chat.id, text=answer, reply_markup=keyboards.Cansel.keyboard)
        bot.register_next_step_handler(msg, send_mailing)

    if message.text == "Удаление пользователей":
        helpers.delete_users_dialog(bot, message)
    if message.text == "Список участников":
        prepared_text = helpers.prepare_users_list_message()
        bot.send_message(chat_id=message.chat.id, text=prepared_text, reply_markup=keyboards.MainMenuForAdmins.keyboard)
    if message.text == "🗂 Таблица игр":
        bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.message_games_table,
                         parse_mode='MarkdownV2', reply_markup=keyboards.MainMenu.keyboard)
    if message.text == "📇 Презентация Сияния":
        bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.message_team_promo,
                         parse_mode='MarkdownV2', reply_markup=keyboards.MainMenu.keyboard)
    if message.text == "🔗 Полезные ссылки":
        bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.message_useful_links,
                         parse_mode='MarkdownV2', reply_markup=keyboards.MainMenu.keyboard,
                         disable_web_page_preview=True)
    if message.text == "🍔 База едален":
        bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.message_food,
                         parse_mode='MarkdownV2', reply_markup=keyboards.MainMenu.keyboard)
    if message.text == "✅ Включить рассылку о мероприятиях":
        is_already_notified = database.check_user_notifications_value(chat_id=message.chat.id)
        if is_already_notified:
            bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.notifications_already_enabled,
                             reply_markup=keyboards.MainMenu.keyboard)
        else:
            database.switch_notifications_flag(chat_id=message.chat.id, new_value=True)
            bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.notifications_enabled,
                             reply_markup=keyboards.MainMenu.keyboard)
    if message.text == "❌ Отменить рассылку о мероприятиях":
        is_already_notified = database.check_user_notifications_value(chat_id=message.chat.id)
        if not is_already_notified:
            bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.notifications_already_disabled,
                             reply_markup=keyboards.MainMenu.keyboard)
        else:
            ans = bot.send_message(chat_id=message.chat.id,
                                   text=constants.TextTemplates.message_notifications_off_confirm,
                                   reply_markup=keyboards.Confirm.keyboard)
            bot.register_next_step_handler(ans, confirm_notifications_off)


def send_mailing(message):
    all_users_chat_ids = database.get_all_users()
    author = message.from_user.username
    if message.text == "Отменить и вернуться в меню":
        bot.send_message(
            chat_id=message.chat.id, text="Возврат в меню", reply_markup=keyboards.MainMenuForAdmins.keyboard
        )
    else:
        for chat_id in all_users_chat_ids:
            print(all_users_chat_ids)
            bot.send_message(chat_id=chat_id,
                             text=constants.TextTemplates.template_for_mailing.format(
                                 author=author, message=message.text)
                             )
            bot.send_message(chat_id=chat_id, text=constants.TextTemplates.send_answer_to,
                             reply_markup=keyboards.MainMenu.keyboard)


def confirm_notifications_off(message):
    if message.text == "Да":
        bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.notifications_disabled,
                         reply_markup=keyboards.MainMenu.keyboard)
        database.switch_notifications_flag(chat_id=message.chat.id, new_value=False)
    else:
        bot.send_message(chat_id=message.chat.id, text=constants.TextTemplates.notifications_not_disabled,
                         reply_markup=keyboards.MainMenu.keyboard)


while True:
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(10)
