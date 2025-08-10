from telegram import Update
from telegram.ext import (
    Application, CommandHandler,MessageHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv
import os
from openai_api import call_openai
from convert_to_pdf import create_resume_from_ai_response

from run_model import predict, model_predict
import re
from parse_pdf import extract_pdf

# Загружаем переменные из .env
load_dotenv()
telegram_token = os.getenv("TELEGRAM_TOKEN")


# 🔹 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я помогу создать тебе резюме!\nДля более точного составление укажи:\n"
        "Профессию, образование, опыт работы (если есть)\n"
        "Если хочешь чтобы я придумал какой-то из пунктов, пропусти его."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    user_doc = update.message.document
    state = False
    if user_doc is not None:
        state = True
        file = await context.bot.get_file(user_doc.file_id)
        file_path = f"{user_doc.file_name}"
        await file.download_to_drive(file_path)
        user_prompt = extract_pdf(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    model, tokenizer = model_predict()

    # Регулярное выражение для удаления ссылок
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|[^\s<>"]+\.[a-zA-Z]{2,}(?:/[^\s<>"]*)?'

    # Функция для удаления ссылок из текста
    def remove_urls(text):
        return re.sub(pattern, '', text)

    if user_doc is None:
        user_prompt = remove_urls(user_prompt)
        predictions = predict(model, tokenizer, user_prompt)

        if predictions == 0:
            await update.message.reply_text(f"Я не понимаю! я не понимаю!\nДля более точного составление укажи:\n"
                                            f"Профессию или область работы, образование (если есть), "
                                            f"опыт работы (если есть)")
            return
    try:
        response = await call_openai(user_prompt, state)
        # Временно получаем результат и проверяем что возвращается
        result = create_resume_from_ai_response(response)

        # Если возвращается кортеж из 2 элементов
        pdf_buffer, parsed_sections = result

        # Отправляем PDF
        await update.message.reply_document(
            document=pdf_buffer,
            filename="resume.pdf",
            caption="Ваш шаблон резюме в формате PDF готов!"
        )
        return
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка, попробуйте позже! {e}")
        return




    # 🔹 Обработка нажатия кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Обязательно: подтверждаем нажатие
    await query.edit_message_text("Ты нажал кнопку ✅")

# 🔹 Основная функция запуска бота
async def main() -> None:
    # Создаём приложение
    app = Application.builder().token(telegram_token).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.PDF & ~filters.COMMAND, handle_message))

    # Запуск бота
    print("Бот запущен...")
    await app.run_polling()

# 🔹 Точка входа
if __name__ == "__main__":
    import asyncio
    import sys

    if sys.platform.startswith('win') and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())

