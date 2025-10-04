#!/usr/bin/env python3
"""
Скрипт для логина в AO3 и сохранения куки для последующего использования
"""

import json
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("save_cookies.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def setup_driver():
    """Настраивает Selenium WebDriver"""
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

        logger.info("✅ WebDriver настроен")
        return driver
    except Exception as e:
        logger.error(f"❌ Ошибка настройки WebDriver: {e}")
        return None


def login_and_save_cookies():
    """Логинится в AO3 и сохраняет куки"""
    config = Config()

    if not config.AO3_USERNAME or not config.AO3_PASSWORD:
        logger.error("❌ Не указаны учетные данные AO3 в .env файле")
        return False

    driver = setup_driver()
    if not driver:
        return False

    try:
        logger.info("🔐 Вход в систему AO3...")
        driver.get("https://archiveofourown.gay/users/login")

        # Ждем загрузки формы входа
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "user[login]"))
        )

        # Ищем видимые поля логина и пароля
        username_field = None
        password_field = None

        # Ищем поле логина (только видимые)
        username_elements = driver.find_elements(
            By.CSS_SELECTOR, "input[name='user[login]']"
        )
        for element in username_elements:
            if element.is_displayed() and element.is_enabled():
                username_field = element
                break

        # Ищем поле пароля (только видимые)
        password_elements = driver.find_elements(
            By.CSS_SELECTOR, "input[name='user[password]']"
        )
        for element in password_elements:
            if element.is_displayed() and element.is_enabled():
                password_field = element
                break

        if not username_field or not password_field:
            logger.error("❌ Поля логина/пароля не найдены")
            return False

        # Заполняем поля
        username_field.clear()
        username_field.send_keys(config.AO3_USERNAME)

        password_field.clear()
        password_field.send_keys(config.AO3_PASSWORD)

        # Ищем кнопку входа (только видимые)
        submit_button = None
        submit_elements = driver.find_elements(
            By.CSS_SELECTOR, "input[type='submit'][name='commit']"
        )
        for element in submit_elements:
            if element.is_displayed() and element.is_enabled():
                submit_button = element
                break

        if not submit_button:
            logger.error("❌ Кнопка входа не найдена")
            return False

        # Нажимаем кнопку
        submit_button.click()

        # Ждем результата
        time.sleep(3)

        # Проверяем результат
        current_url = driver.current_url
        if "login" not in current_url.lower():
            logger.info("✅ Успешный вход в систему")

            # Сохраняем куки
            cookies = driver.get_cookies()
            with open("ao3_cookies.json", "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)

            logger.info("🍪 Куки сохранены в ao3_cookies.json")
            return True
        else:
            logger.error("❌ Остались на странице логина")
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка входа в систему: {e}")
        return False

    finally:
        driver.quit()


if __name__ == "__main__":
    print("🍪 Сохранение куки AO3...")
    print("=" * 50)

    if login_and_save_cookies():
        print("✅ Куки успешно сохранены!")
        print("📁 Файл: ao3_cookies.json")
        print("🔄 Теперь можно использовать эти куки для входа")
    else:
        print("❌ Не удалось сохранить куки")
