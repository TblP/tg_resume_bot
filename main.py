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

load_dotenv()
telegram_token = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я помогу создать тебе резюме!\nДля более точного составление укажи:\n"
        "Профессию, образование, опыт работы (если есть)\n"
        "Если хочешь чтобы я придумал какой-то из пунктов, пропусти его."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений из бота
            Args:
                update сообщение от пользователя

            Returns:
                отправляет документ пользователю

                """
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

    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|[^\s<>"]+\.[a-zA-Z]{2,}(?:/[^\s<>"]*)?'

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

        result = create_resume_from_ai_response(response)

        pdf_buffer, parsed_sections = result

        await update.message.reply_document(
            document=pdf_buffer,
            filename="resume.pdf",
            caption="Ваш шаблон резюме в формате PDF готов!"
        )
        return
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка, попробуйте позже! {e}")
        return

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Ты нажал кнопку ✅")


async def main() -> None:

    app = Application.builder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.PDF & ~filters.COMMAND, handle_message))


    print("Бот запущен...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    import sys

    if sys.platform.startswith('win') and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())

