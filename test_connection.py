#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к Telegram
"""

import asyncio
import sys

from telegram_bot import TelegramNotifier


async def test_telegram():
    """Тестирует подключение к Telegram"""
    print("🔍 Тестирую подключение к Telegram...")

    telegram = TelegramNotifier()

    if await telegram.test_connection():
        print("✅ Подключение к Telegram успешно!")
        return True
    else:
        print("❌ Ошибка подключения к Telegram")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_telegram())
    sys.exit(0 if success else 1)
