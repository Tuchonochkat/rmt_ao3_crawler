#!/usr/bin/env python3
"""
AO3 Crawler - Краулер для Archive of Our Own
Автоматически ищет новые работы по заданным тегам/фандомам и отправляет уведомления в Telegram
"""

import logging
import sys
import time

from ao3_crawler import AO3Crawler
from config import Config
from telegram_bot import TelegramNotifier


def setup_logging():
    """Настраивает логирование"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("crawler.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def check_config():
    """Проверяет корректность конфигурации"""
    config = Config()
    required_vars = [
        "AO3_USERNAME",
        "AO3_PASSWORD",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHANNEL_ID",
    ]

    missing_vars = []
    for var in required_vars:
        if not getattr(config, var):
            missing_vars.append(var)

    if missing_vars:
        print(
            f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}"
        )
        print("Создайте файл .env и заполните необходимые переменные")
        return False

    if not config.SEARCH_TAGS and not config.SEARCH_FANDOMS:
        print("❌ Необходимо указать теги или фандомы для поиска")
        return False

    return True


async def main():
    """Основная функция краулера"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Запуск AO3 Crawler...")

    # Проверяем конфигурацию
    if not check_config():
        logger.error("❌ Неверная конфигурация. Завершение работы.")
        return

    crawler = AO3Crawler()
    telegram = TelegramNotifier()

    # Тестируем подключение к Telegram
    logger.info("🔍 Проверяю подключение к Telegram...")
    if not await telegram.test_connection():
        logger.error("❌ Не удалось подключиться к Telegram")
        return

    logger.info("✅ Подключение к Telegram успешно")

    try:
        # Запускаем краулер
        logger.info("🕷️ Запускаю краулер AO3...")
        works = crawler.run_crawler()

        if works:
            logger.info(f"📚 Найдено {len(works)} новых работ")

            # Отправляем в Telegram
            logger.info("📤 Отправляю уведомления в Telegram...")
            await telegram.send_multiple_works(works)

            # Отмечаем работы как опубликованные
            for work in works:
                crawler.mark_work_as_posted(work)

            logger.info("✅ Все работы обработаны и отправлены")
        else:
            logger.info("ℹ️ Новых работ не найдено")

    except KeyboardInterrupt:
        logger.info("⏹️ Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        logger.info("🏁 Краулер завершил работу")


def run_continuous():
    """Запускает краулер в непрерывном режиме"""
    config = Config()
    logger = logging.getLogger(__name__)

    logger.info(
        f"🔄 Запуск в непрерывном режиме (интервал: {config.REQUEST_DELAY} сек)"
    )

    while True:
        try:
            asyncio.run(main())
            logger.info(
                f"⏰ Ожидание {config.REQUEST_DELAY} секунд до следующего запуска..."
            )
            time.sleep(config.REQUEST_DELAY)
        except KeyboardInterrupt:
            logger.info("⏹️ Получен сигнал остановки")
            break
        except Exception as e:
            logger.error(f"❌ Ошибка в непрерывном режиме: {e}")
            logger.info(f"⏰ Ожидание {config.REQUEST_DELAY} секунд перед повтором...")
            time.sleep(config.REQUEST_DELAY)


if __name__ == "__main__":
    import asyncio

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous()
    else:
        asyncio.run(main())
