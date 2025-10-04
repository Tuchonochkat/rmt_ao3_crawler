#!/usr/bin/env python3
"""
Простой тест логина на AO3 с доменом .gay
Только проверяет успешность входа без лишнего анализа
"""

import logging
import time
from typing import Tuple

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config


class SimpleLoginTest:
    """
    Простой тест логина на AO3
    """

    def __init__(self, username: str = None, password: str = None):
        self.username = username or Config.AO3_USERNAME
        self.password = password or Config.AO3_PASSWORD
        self.driver = None
        self.setup_logging()

    def setup_logging(self):
        """Настраивает логирование"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("simple_login_test.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self) -> bool:
        """Настраивает Selenium WebDriver"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-images")
            # НЕ отключаем JS, так как он может быть нужен для логина

            # Используем случайный User-Agent
            ua = UserAgent()
            options.add_argument(f"--user-agent={ua.random}")

            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            self.logger.info("✅ WebDriver настроен")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки WebDriver: {e}")
            return False

    def test_login(self) -> Tuple[bool, str]:
        """Тестирует логин"""
        try:
            self.logger.info("🔐 Тестируем логин...")

            # Переходим на страницу логина
            login_url = "https://archiveofourown.gay/users/login"
            self.driver.get(login_url)

            # Ждем загрузки формы
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "user[login]"))
            )

            # Ищем видимые поля логина и пароля
            username_field = None
            password_field = None

            # Ищем поле логина (только видимые)
            username_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "input[name='user[login]']"
            )
            for element in username_elements:
                if element.is_displayed() and element.is_enabled():
                    username_field = element
                    break

            # Ищем поле пароля (только видимые)
            password_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "input[name='user[password]']"
            )
            for element in password_elements:
                if element.is_displayed() and element.is_enabled():
                    password_field = element
                    break

            if not username_field or not password_field:
                return False, "Поля логина/пароля не найдены"

            # Заполняем поля
            username_field.clear()
            username_field.send_keys(self.username)

            password_field.clear()
            password_field.send_keys(self.password)

            # Ищем кнопку входа (только видимые)
            submit_button = None
            submit_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "input[type='submit'][name='commit']"
            )
            for element in submit_elements:
                if element.is_displayed() and element.is_enabled():
                    submit_button = element
                    break

            if not submit_button:
                return False, "Кнопка входа не найдена"

            # Нажимаем кнопку
            submit_button.click()

            # Ждем результата
            time.sleep(3)

            # Проверяем результат
            current_url = self.driver.current_url
            self.logger.info(f"🔗 Текущий URL: {current_url}")

            # Проверяем на ошибки
            error_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".error, .alert, .warning"
            )
            if error_elements:
                error_text = error_elements[0].text
                return False, f"Ошибка входа: {error_text}"

            # Проверяем успешность входа
            if "login" not in current_url.lower():
                self.logger.info("✅ Успешный вход в систему")
                return True, "Успешный вход"
            else:
                return False, "Остались на странице логина"

        except Exception as e:
            self.logger.error(f"❌ Ошибка при тестировании логина: {e}")
            return False, str(e)

    def run_test(self) -> bool:
        """Запускает тест логина"""
        try:
            self.logger.info("🚀 Запускаем тест логина...")

            # Настраиваем драйвер
            if not self.setup_driver():
                return False

            # Тестируем логин
            success, message = self.test_login()
            self.logger.info(f"🔐 Результат: {success} - {message}")

            return success

        except Exception as e:
            self.logger.error(f"❌ Ошибка в тесте: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def __del__(self):
        if self.driver:
            self.driver.quit()


def main():
    """Основная функция для тестирования логина"""
    print("🔍 Простой тест логина на AO3 с доменом .gay")

    # Проверяем наличие учетных данных
    if not Config.AO3_USERNAME or not Config.AO3_PASSWORD:
        print("❌ Учетные данные не найдены в конфиге")
        print("   Убедитесь, что AO3_USERNAME и AO3_PASSWORD установлены в .env")
        return

    # Создаем тестер
    tester = SimpleLoginTest()

    # Запускаем тест
    success = tester.run_test()

    if success:
        print("✅ Тест логина прошел успешно")
    else:
        print("❌ Тест логина не прошел")
        print("   Проверьте логи в simple_login_test.log")


if __name__ == "__main__":
    main()
