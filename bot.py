from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = '8157906074:AAGuP4FGIypt9RIII4W_s35luxDL0_-dONQ'
ADMIN_ID = 6794301033  # Замени на свой Telegram ID

users_data = {}

routes = {
    "route1": {
        "name": "Горы и каньоны",
        "stops": [
            "📍 Сулакский каньон — один из самых глубоких в мире.",
            "📍 Гора Шалбуздаг — священное место, к которому совершают паломничество.",
            "📍 Карадахская теснина — узкий и живописный проход между скал."
        ],
        "test": [
            {
                "q": "Как называется один из самых глубоких каньонов в мире в Дагестане?",
                "a": "Сулакский каньон"
            }
        ]
    },
    "route2": {
        "name": "Море и города",
        "stops": [
            "📍 Каспийское море — крупнейшее замкнутое море на планете.",
            "📍 Дербент — один из древнейших городов России.",
            "📍 Махачкала — столица Дагестана, культурный центр."
        ],
        "test": [
            {
                "q": "Как называется столица Дагестана?",
                "a": "Махачкала"
            }
        ]
    },
    "route3": {
        "name": "История и культура",
        "stops": [
            "📍 Аул Кубачи — знаменит своими ремесленниками.",
            "📍 Хунзах — родина поэтов и горской культуры.",
            "📍 Гуниб — место исторических сражений."
        ],
        "test": [
            {
                "q": "Какой аул знаменит ювелирами и оружейниками?",
                "a": "Кубачи"
            }
        ]
    }
}

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    users_data[user_id] = {"path": None, "step": 0, "papakhas": 0}
    buttons = [
        [InlineKeyboardButton(routes[r]["name"], callback_data=f"start_{r}")]
        for r in routes
    ]
    update.message.reply_text("Добро пожаловать в путеводитель по Дагестану! Выберите маршрут:", reply_markup=InlineKeyboardMarkup(buttons))

def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    query.answer()

    if data.startswith("start_"):
        route_key = data.split("_")[1]
        users_data[user_id]["path"] = route_key
        users_data[user_id]["step"] = 0
        send_step(query, user_id)
    elif data == "next":
        users_data[user_id]["step"] += 1
        send_step(query, user_id)
    elif data == "back":
        users_data[user_id]["step"] -= 1
        send_step(query, user_id)
    elif data == "menu":
        start(update, context)
    elif data == "start_test":
        send_test(query, user_id)
    elif data == "send_photos":
        query.edit_message_text("📸 Задание:\n1. Сфотографируйте одно из мест маршрута.\n2. Сделайте селфи с природой Дагестана.\n\nОтправьте 2 фото боту.")
        users_data[user_id]["awaiting_photos"] = True
    elif data == "check_reward":
        check_certificate(query, user_id)

def send_step(query, user_id):
    route_key = users_data[user_id]["path"]
    step = users_data[user_id]["step"]
    stops = routes[route_key]["stops"]

    if step < 0: step = 0
    if step >= len(stops):
        query.edit_message_text(
            f"🏁 Вы прошли маршрут: {routes[route_key]['name']}!\nПора пройти тест.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧪 Пройти тест", callback_data="start_test")]
            ])
        )
        return

    text = stops[step]
    buttons = []
    if step > 0:
        buttons.append(InlineKeyboardButton("◀️ Назад", callback_data="back"))
    if step < len(stops) - 1:
        buttons.append(InlineKeyboardButton("▶️ Далее", callback_data="next"))
    else:
        buttons.append(InlineKeyboardButton("✅ Завершить", callback_data="next"))
    buttons.append(InlineKeyboardButton("📍 В меню", callback_data="menu"))

    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([buttons]))

def send_test(query, user_id):
    route_key = users_data[user_id]["path"]
    question = routes[route_key]["test"][0]
    context = query.message.bot
    context.send_message(user_id, f"🧪 Вопрос:\n{question['q']}")
    users_data[user_id]["awaiting_answer"] = question["a"]

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data = users_data.get(user_id, {})

    if user_data.get("awaiting_answer"):
        correct_answer = user_data["awaiting_answer"]
        if correct_answer.lower() in update.message.text.lower():
            users_data[user_id]["papakhas"] += 5
            update.message.reply_text(f"✅ Верно! Вы получили 5 папах. Всего: {users_data[user_id]['papakhas']}")
            update.message.reply_text("📸 Выполните задания с фото:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Отправить фото", callback_data="send_photos")],
                [InlineKeyboardButton("🎖 Проверить награды", callback_data="check_reward")]
            ]))
        else:
            update.message.reply_text("❌ Неверно. Попробуйте еще.")
        users_data[user_id]["awaiting_answer"] = None
    elif user_data.get("awaiting_photos"):
        if update.message.photo:
            context.bot.send_message(chat_id=ADMIN_ID, text=f"📷 Фото от {update.effective_user.username or user_id}:")
            context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            update.message.reply_text("✅ Фото отправлено.")
        else:
            update.message.reply_text("Пожалуйста, отправьте именно фото.")
    else:
        update.message.reply_text("Выберите маршрут с помощью команд.")

def check_certificate(query, user_id):
    if users_data[user_id]["papakhas"] >= 10:
        query.edit_message_text("🎉 Поздравляем! Вы собрали 10 папах и получаете сертификат!")
    else:
        query.edit_message_text(f"У вас {users_data[user_id]['papakhas']} папах. Нужно 10 для сертификата.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
