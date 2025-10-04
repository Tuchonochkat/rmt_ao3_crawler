import asyncio
import logging

from telegram import Bot
from telegram.error import TelegramError

from config import Config


class TelegramNotifier:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(token=self.config.TELEGRAM_BOT_TOKEN)
        self.logger = logging.getLogger(__name__)

    def format_work_message(self, work_info):
        """Форматирует сообщение о работе для отправки в Telegram"""
        # Форматируем согласно требованиям
        message = f"✨✨✨ <a href='{work_info['url']}'><b>{work_info['title']}</b></a> ✨✨✨\n\n"
        message += f"👤 <b>Автор:</b> {work_info['author']}\n"

        # Фандомы
        if work_info.get("fandoms"):
            fandoms = ", ".join(work_info["fandoms"])
            message += f"🌍<b> Фандом:</b> {fandoms}\n"

        # Отношения
        if work_info.get("relationships"):
            relationships_str = ", ".join(work_info["relationships"])
            message += f"💕<b> Пейринг: {relationships_str}</b>\n"

        # Рейтинг
        if work_info.get("rating"):
            message += f"⭐️<b> Рейтинг:</b> {work_info['rating']}\n"

        # Предупреждения
        if work_info.get("warnings"):
            warnings_str = ", ".join(work_info["warnings"])
            if warnings_str != "No Archive Warnings Apply":
                message += f"⚠️<b> Предупреждения:</b> {warnings_str}\n"

        # Статистика
        if work_info.get("stats", {}).get("words"):
            message += f"📝<b> Кол-во слов:</b> {work_info['stats']['words']}\n"

        # Теги
        if work_info.get("tags"):
            tags_str = ", ".join(work_info["tags"])
            message += f"🏷️<b> Тэги и персонажи:</b> {tags_str}\n"

        # Описание
        if work_info.get("summary"):
            message += f"📖<b> Описание:</b> {work_info['summary']}\n"

        return message

    async def send_work_notification(self, work_info):
        """Отправляет уведомление о новой работе в Telegram канал"""
        try:
            message = self.format_work_message(work_info)

            await self.bot.send_message(
                chat_id=self.config.TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=False,
            )

            self.logger.info(f"Отправлено уведомление о работе: {work_info['title']}")
            return True

        except TelegramError as e:
            self.logger.error(f"Ошибка при отправке в Telegram: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при отправке в Telegram: {e}")
            return False

    async def send_multiple_works(self, works):
        """Отправляет уведомления о нескольких работах"""
        if not works:
            self.logger.info("Нет работ для отправки")
            return

        self.logger.info(f"Отправляю {len(works)} работ в Telegram...")

        for i, work in enumerate(works):
            try:
                success = await self.send_work_notification(work)
                if success:
                    self.logger.info(f"Работа {i+1}/{len(works)} отправлена успешно")
                else:
                    self.logger.warning(
                        f"Не удалось отправить работу {i+1}/{len(works)}"
                    )

                # Небольшая задержка между отправками
                if i < len(works) - 1:
                    await asyncio.sleep(2)

            except Exception as e:
                self.logger.error(f"Ошибка при отправке работы {i+1}: {e}")
                continue

    def send_works_sync(self, works):
        """Синхронная обертка для отправки работ"""
        return asyncio.run(self.send_multiple_works(works))

    async def test_connection(self):
        """Тестирует соединение с Telegram"""
        try:
            bot_info = await self.bot.get_me()
            self.logger.info(f"Telegram бот подключен: @{bot_info.username}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
