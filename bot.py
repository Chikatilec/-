from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

BOT_TOKEN = "8157906074:AAGuP4FGIypt9RIII4W_s35luxDL0_-dONQ"
ADMIN_ID = 6794301033

# Данные
routes = {
    "Маршрут 1": [
        "Добро пожаловать на маршрут 1 по Дагестану! Здесь вы увидите горы и водопады.",
        "Продолжаем маршрут 1: красивые ущелья и старинные деревни.",
        "Финал маршрута 1. Готовы пройти тест и задания?"
    ],
    "Маршрут 2": [
        "Маршрут 2 — пляжи Каспийского моря и старинные крепости.",
        "Пляжи и природа продолжаются, наслаждайтесь видом.",
        "Конец маршрута 2. Спасибо за путешествие!"
    ],
    "Маршрут 3": [
        "Маршрут 3 — музеи и культурные памятники Махачкалы.",
        "Посещение местных рынков и мастерских.",
        "Заключительный этап маршрута 3."
    ]
}

test_questions = [
    {
        "question": "Как называется главная гора, которую вы видели на маршруте 1?",
        "options": ["Гора Казбек", "Гора Базардюзю", "Гора Эльбрус"],
        "correct": "Гора Базардюзю"
    },
    {
        "question": "Какое природное явление вы видели в ущельях?",
        "options": ["Водопад", "Пустыня", "Ледник"],
        "correct": "Водопад"
    }
]

photo_tasks = [
    "Отправьте фотографию горы, которую вы увидели.",
    "Отправьте фотографию местного памятника или культурного объекта."
]

user_data = {}

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id] = {"state": "main", "route": None, "step": 0, "points": 0, "test_step": 0, "test_correct": 0, "photo_task": 0}
    keyboard = [["Маршрут 1", "Маршрут 2", "Маршрут 3"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Добро пожаловать в путеводитель по Дагестану! Выберите маршрут:", reply_markup=reply_markup)

def route_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text
    if text in routes:
        user_data[user_id]["state"] = "route"
        user_data[user_id]["route"] = text
        user_data[user_id]["step"] = 0
        keyboard = [["Далее", "Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(routes[text][0], reply_markup=reply_markup)
    elif text == "Далее":
        if user_data[user_id]["state"] == "route":
            route = user_data[user_id]["route"]
            user_data[user_id]["step"] += 1
            step = user_data[user_id]["step"]
            if step < len(routes[route]):
                keyboard = [["Далее", "Назад"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                update.message.reply_text(routes[route][step], reply_markup=reply_markup)
            else:
                if route == "Маршрут 1":
                    user_data[user_id]["state"] = "test"
                    user_data[user_id]["test_step"] = 0
                    user_data[user_id]["test_correct"] = 0
                    send_test_question(update, context)
                else:
                    user_data[user_id]["state"] = "photo"
                    user_data[user_id]["photo_task"] = 0
                    update.message.reply_text("Маршрут завершён! Теперь выполните фото-задания.")
                    update.message.reply_text(photo_tasks[0])
        else:
            update.message.reply_text("Выберите маршрут.")
    elif text == "Назад":
        user_data[user_id]["state"] = "main"
        user_data[user_id]["route"] = None
        user_data[user_id]["step"] = 0
        keyboard = [["Маршрут 1", "Маршрут 2", "Маршрут 3"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Вы вернулись в главное меню. Выберите маршрут:", reply_markup=reply_markup)
    else:
        update.message.reply_text("Пожалуйста, выберите опцию из меню.")

def send_test_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    step = user_data[user_id]["test_step"]
    q = test_questions[step]
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(q["question"], reply_markup=reply_markup)

def test_answer_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    answer = query.data
    step = user_data[user_id]["test_step"]
    correct = test_questions[step]["correct"]
    if answer == correct:
        user_data[user_id]["test_correct"] += 1
        query.answer("Правильно!")
    else:
        query.answer("Неправильно!")
    user_data[user_id]["test_step"] += 1
    if user_data[user_id]["test_step"] < len(test_questions):
        send_test_question(update, context)
    else:
        user_data[user_id]["state"] = "photo"
        user_data[user_id]["photo_task"] = 0
        if user_data[user_id]["test_correct"] > 0:
            user_data[user_id]["points"] += 5
            context.bot.send_message(user_id, f"Тест пройден! +5 папах. Всего папах: {user_data[user_id]['points']}")
            if user_data[user_id]["points"] >= 10:
                context.bot.send_message(user_id, "Поздравляем! Вы можете получить сертификат!")
        else:
            context.bot.send_message(user_id, "Тест завершён. Папах не начислено.")
        context.bot.send_message(user_id, "Теперь выполните фото-задания.")
        context.bot.send_message(user_id, photo_tasks[0])
    query.edit_message_reply_markup(reply_markup=None)

def photo_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_data.get(user_id, {}).get("state") != "photo":
        update.message.reply_text("Фото сейчас не требуется.")
        return
    task_num = user_data[user_id]["photo_task"]
    photo_file_id = update.message.photo[-1].file_id
    context.bot.send_photo(ADMIN_ID, photo_file_id, caption=f"Фото от {update.effective_user.full_name} — задание: {photo_tasks[task_num]}")
    user_data[user_id]["photo_task"] += 1
    if user_data[user_id]["photo_task"] < len(photo_tasks):
        update.message.reply_text(f"Фото получено! Следующее задание:\n{photo_tasks[user_data[user_id]['photo_task']]}")
    else:
        user_data[user_id]["points"] += 5
        update.message.reply_text(f"Все фото сданы! +5 папах. Всего папах: {user_data[user_id]['points']}")
        if user_data[user_id]["points"] >= 10:
            update.message.reply_text("Поздравляем! Вы можете получить сертификат!")
        user_data[user_id]["state"] = "main"
        user_data[user_id]["route"] = None
        user_data[user_id]["step"] = 0
        user_data[user_id]["photo_task"] = 0
        keyboard = [["Маршрут 1", "Маршрут 2", "Маршрут 3"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Возвращаемся в главное меню.", reply_markup=reply_markup)

def fallback(update: Update, context: CallbackContext):
    update.message.reply_text("Пожалуйста, используйте кнопки меню.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, route_handler))
    dp.add_handler(CallbackQueryHandler(test_answer_handler))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))
    dp.add_handler(MessageHandler(Filters.command, fallback))

    updater.start_polling()
    print("Бот запущен")
    updater.idle()

if __name__ == "__main__":
    main()
