import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Меню и данные (упрощённо)
user_data = {}

main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add("Маршрут 1", "Маршрут 2", "Маршрут 3")
back_button = KeyboardButton("Назад")

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

def test_keyboard(options):
    kb = InlineKeyboardMarkup()
    for opt in options:
        kb.add(InlineKeyboardButton(opt, callback_data=f"test_answer:{opt}"))
    return kb

# Хендлеры

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {
        "state": "main",
        "route": None,
        "route_step": 0,
        "points": 0,
        "test_step": 0,
        "test_correct": 0,
        "photo_task": 0
    }
    await message.answer("Добро пожаловать в путеводитель по Дагестану! Выберите маршрут:", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text in routes.keys())
async def start_route(message: types.Message):
    user = user_data.get(message.from_user.id)
    user["state"] = "route"
    user["route"] = message.text
    user["route_step"] = 0
    await message.answer(routes[user["route"]][0], reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(back_button, KeyboardButton("Далее")))

@dp.message_handler(lambda m: m.text == "Назад")
async def go_back(message: types.Message):
    user = user_data.get(message.from_user.id)
    if not user:
        await start_handler(message)
        return

    if user["state"] == "route":
        user["state"] = "main"
        user["route"] = None
        user["route_step"] = 0
        await message.answer("Вы вернулись в главное меню. Выберите маршрут:", reply_markup=main_menu)
    elif user["state"] == "test" or user["state"] == "photo_tasks":
        user["state"] = "main"
        await message.answer("Вы вышли в главное меню. Выберите маршрут:", reply_markup=main_menu)
    else:
        await message.answer("Вы в главном меню.", reply_markup=main_menu)

@dp.message_handler(lambda m: m.text == "Далее")
async def route_next_step(message: types.Message):
    user = user_data.get(message.from_user.id)
    if not user or user["state"] != "route":
        await message.answer("Пожалуйста, выберите маршрут.")
        return

    user["route_step"] += 1
    route = user["route"]
    step = user["route_step"]

    if step < len(routes[route]):
        await message.answer(routes[route][step], reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(back_button, KeyboardButton("Далее")))
    else:
        if route == "Маршрут 1":
            user["state"] = "test"
            user["test_step"] = 0
            user["test_correct"] = 0
            q = test_questions[0]
            await message.answer("Маршрут завершён! Пройдите тест:", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(back_button))
            await message.answer(q["question"], reply_markup=test_keyboard(q["options"]))
        else:
            user["state"] = "photo_tasks"
            user["photo_task"] = 0
            await message.answer("Маршрут завершён! Теперь выполните фото-задания.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(back_button))
            await message.answer(photo_tasks[0])

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("test_answer:"))
async def process_test_answer(callback_query: types.CallbackQuery):
    user = user_data.get(callback_query.from_user.id)
    if not user or user["state"] != "test":
        await callback_query.answer("Тест не активен.")
        return

    answer = callback_query.data.split(":")[1]
    step = user["test_step"]
    correct = test_questions[step]["correct"]

    if answer == correct:
        user["test_correct"] += 1
        await callback_query.answer("Правильно!")
    else:
        await callback_query.answer("Неправильно!")

    user["test_step"] += 1
    if user["test_step"] < len(test_questions):
        q = test_questions[user["test_step"]]
        await bot.send_message(callback_query.from_user.id, q["question"], reply_markup=test_keyboard(q["options"]))
    else:
        user["state"] = "photo_tasks"
        user["photo_task"] = 0
        if user["test_correct"] > 0:
            user["points"] += 5
            await bot.send_message(callback_query.from_user.id, f"Тест пройден! +5 папах. Всего папах: {user['points']}")
            if user["points"] >= 10:
                await bot.send_message(callback_query.from_user.id, "Поздравляем! Вы можете получить сертификат!")
        else:
            await bot.send_message(callback_query.from_user.id, "Тест завершён. Папах не начислено.")

        await bot.send_message(callback_query.from_user.id, "Теперь выполните фото-задания.")
        await bot.send_message(callback_query.from_user.id, photo_tasks[0])

@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def photo_handler(message: types.Message):
    user = user_data.get(message.from_user.id)
    if not user or user["state"] != "photo_tasks":
        await message.answer("Фото сейчас не требуется.")
        return

    task_num = user["photo_task"]
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"Фото от {message.from_user.full_name} — задание: {photo_tasks[task_num]}")

    user["photo_task"] += 1
    if user["photo_task"] < len(photo_tasks):
        await message.answer(f"Фото получено! Следующее задание:\n{photo_tasks[user['photo_task']]}")
    else:
        user["points"] += 5
        await message.answer(f"Все фото сданы! +5 папах. Всего папах: {user['points']}")
        if user["points"] >= 10:
            await message.answer("Поздравляем! Вы можете получить сертификат!")
        user["state"] = "main"
        user["route"] = None
        user["route_step"] = 0
        user["photo_task"] = 0
        await message.answer("Возвращаемся в главное меню.", reply_markup=main_menu)

@dp.message_handler()
async def fallback_handler(message: types.Message):
    await message.answer("Пожалуйста, выберите опцию из меню.", reply_markup=main_menu)

if __name__ == "__main__":
    print("Запуск бота...")
    executor.start_polling(dp, skip_updates=True)
