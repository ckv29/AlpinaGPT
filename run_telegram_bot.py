# run_telegram_bot.py

import os
import sys
import asyncio
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AlpinaGPT.settings')
django.setup()

from api.telegram_bot import get_telegram_app


async def main():
    app = get_telegram_app()
    print("✅ Telegram бот запущен в режиме long polling...")
    print("Нажмите Ctrl+C для остановки.")

    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        # Ждём прерывания
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    finally:
        # Корректное завершение
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    # Для Windows: фикс асинхронности
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Бот остановлен.")