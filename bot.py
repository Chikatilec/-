from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io
import os

BOT_TOKEN = 'твой_токен_от_BotFather'  # Вставь сюда свой токен
ADMIN_ID = 123456789  # Вставь сюда свой Telegram ID

# Проверка, что файл — изображение через Pillow
def is_image_file(file_bytes):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        return True
    except Exception:
        return False

# Главное меню
menu_keyboard = [
    [KeyboardButton('Путь 1'), KeyboardButton('Путь 2')],
    [KeyboardButton('Путь 3')],
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я — путеводитель по Дагестану.\nВыбери путь для знакомства с красивыми местами:",
        reply_markup=menu_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'Путь 1':
        await update.message.reply_text("Описание Пути 1 ...\n\n(текст с интересными местами)")
        # Здесь можно добавить кнопки для перехода или задания
    elif text == 'Путь 2':
        await update.message.reply_text("Описание Пути 2 ...\n\n(текст с интересными местами)")
    elif text == 'Путь 3':
        await update.message.reply_text("Описание Пути 3 ...\n\n(текст с интересными местами)")
    else:
        await update.message.reply_text("Пожалуйста, выбери путь из меню.")

# Обработка фото от пользователя
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_bytes = await photo_file.download_as_bytearray()

    if is_image_file(file_bytes):
        # Перешлём фото на твой аккаунт (админский)
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_bytes,
                                     caption=f"Фото от @{update.message.from_user.username} ({update.message.from_user.id})")
        await update.message.reply_text("Спасибо за фото! Оно принято.")
    else:
        await update.message.reply_text("Похоже, это не изображение. Попробуй отправить фото.")

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
