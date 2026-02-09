# api/telegram_bot.py
from asgiref.sync import sync_to_async
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from django.conf import settings
from .models import Bot
from .yandex_gpt_service import generate_response_with_system

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я бот на базе Alpina.GPT. Напиши что-нибудь!")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    logger.info(f"📩 Получено сообщение от {chat_id}: '{user_message}'")

    # Используем sync_to_async для ORM
    try:
        bot = await sync_to_async(Bot.objects.get)(telegram_token=settings.TELEGRAM_BOT_TOKEN)
        logger.info(f"✅ Найден бот: {bot.name}")
    except Bot.DoesNotExist:
        logger.error("❌ Бот с таким токеном НЕ НАЙДЕН в базе данных!")
        await update.message.reply_text("Бот не настроен.")
        return

    try:
        response_text = generate_response_with_system(
            system_prompt=bot.system_prompt,
            user_prompt=user_message,
            model=bot.gpt_model,
            temperature=bot.temperature,
            max_tokens=bot.max_tokens
        )
        logger.info(f"📤 Отправляем ответ: '{response_text[:50]}...'")
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"💥 Ошибка GPT: {e}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

def get_telegram_app():
    """Создаёт и возвращает Telegram Application"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан в настройках")

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    return application