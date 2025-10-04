#!/usr/bin/env python3
"""
Тест отправки в Telegram - отправляем только первую работу из JSON
"""

import json
import logging

from telegram_bot import TelegramNotifier


def setup_logging():
    """Настраивает логирование"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("test_telegram.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def load_works_from_json():
    """Загружает работы из JSON файла"""
    try:
        with open("improved_search.json", "r", encoding="utf-8") as f:
            works = json.load(f)
        print(f"📚 Загружено {len(works)} работ из JSON")
        return works
    except Exception as e:
        print(f"❌ Ошибка загрузки JSON: {e}")
        return []


def test_telegram_connection():
    """Тестирует подключение к Telegram"""
    print("🔍 Тестируем подключение к Telegram...")

    notifier = TelegramNotifier()

    # Тестируем соединение
    import asyncio

    success = asyncio.run(notifier.test_connection())

    if success:
        print("✅ Подключение к Telegram успешно")
        return True
    else:
        print("❌ Ошибка подключения к Telegram")
        return False


def send_first_work():
    """Отправляет первую работу в Telegram"""
    print("📤 Отправляем первую работу в Telegram...")

    # Загружаем работы
    works = load_works_from_json()
    if not works:
        print("❌ Нет работ для отправки")
        return False

    # Берем только первую работу
    first_work = works[0]
    print(f"📝 Отправляем: {first_work['title']}")

    # Создаем уведомлятель
    notifier = TelegramNotifier()

    # Отправляем
    import asyncio

    success = asyncio.run(notifier.send_work_notification(first_work))

    if success:
        print("✅ Работа отправлена успешно")
        return True
    else:
        print("❌ Ошибка отправки работы")
        return False


def main():
    """Основная функция тестирования"""
    print("🧪 Тест Telegram-бота")
    print("=" * 50)

    setup_logging()

    # 1. Тестируем подключение
    if not test_telegram_connection():
        print("❌ Не удалось подключиться к Telegram")
        print("   Проверьте TELEGRAM_BOT_TOKEN и TELEGRAM_CHANNEL_ID в .env")
        return

    # 2. Отправляем первую работу
    if send_first_work():
        print("🎉 Тест завершен успешно!")
    else:
        print("❌ Ошибка при отправке работы")


if __name__ == "__main__":
    main()
