#!/usr/bin/env python3
"""
Улучшенный краулер AO3 с разделением получения HTML и парсинга
Сначала получаем HTML, затем парсим его отдельно
"""

import json
import logging
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import Config


class ImprovedCrawler:
    """
    Улучшенный краулер AO3 с разделением получения HTML и парсинга
    """

    def __init__(self, username=None, password=None):
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
                logging.FileHandler("improved_crawler.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def setup_driver(self):
        """Настраивает Selenium WebDriver"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

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

    def load_cookies(self) -> bool:
        """Загружает сохраненные куки"""
        try:
            import json
            import os

            cookies_file = "ao3_cookies.json"
            if not os.path.exists(cookies_file):
                self.logger.warning("⚠️ Файл куки не найден, требуется логин")
                return False

            # Загружаем куки
            with open(cookies_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)

            # Переходим на главную страницу AO3
            self.driver.get("https://archiveofourown.gay")

            # Добавляем куки
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.logger.debug(
                        f"Не удалось добавить куки {cookie.get('name', 'unknown')}: {e}"
                    )

            # Перезагружаем страницу с куки
            self.driver.refresh()
            time.sleep(2)

            # Проверяем, что мы залогинены
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                self.logger.info("✅ Успешная загрузка куки")
                return True
            else:
                self.logger.warning("⚠️ Куки недействительны, требуется повторный логин")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки куки: {e}")
            return False

    def login(self) -> bool:
        """Входит в систему AO3"""
        try:
            self.logger.info("🔐 Вход в систему...")
            self.driver.get("https://archiveofourown.gay/users/login")

            # Ждем загрузки формы входа
            WebDriverWait(self.driver, 10).until(
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
                self.logger.error("❌ Поля логина/пароля не найдены")
                return False

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
                self.logger.error("❌ Кнопка входа не найдена")
                return False

            # Нажимаем кнопку
            submit_button.click()

            # Ждем результата
            time.sleep(3)

            # Проверяем результат
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                self.logger.info("✅ Успешный вход в систему")
                return True
            else:
                self.logger.error("❌ Остались на странице логина")
                return False

        except Exception as e:
            self.logger.error(f"❌ Ошибка входа в систему: {e}")
            return False

    def build_search_url(self, fandoms: List[str] = None) -> str:
        """Строит URL для поиска"""
        base_url = "https://archiveofourown.gay/works/search"
        params = {
            "work_search[sort_column]": "revised_at",
            "work_search[sort_direction]": "desc",
            "commit": "Search",
        }

        if fandoms:
            params["work_search[fandom_names]"] = fandoms[0]  # Берем первый фандом

        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"

        self.logger.info(f"🔗 Построен URL для поиска: {url}")
        return url

    def get_search_html(self, fandoms: List[str] = None) -> str:
        """Получает HTML страницы поиска"""
        try:
            # Строим URL для поиска
            search_url = self.build_search_url(fandoms=fandoms)

            # Переходим на страницу поиска
            self.driver.get(search_url)

            # Ждем загрузки результатов
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.work.blurb.group"))
            )

            self.logger.info("✅ Результаты поиска загружены")

            # Получаем HTML
            html_content = self.driver.page_source
            self.logger.info(f"📄 HTML получен ({len(html_content)} символов)")

            return html_content

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения HTML: {e}")
            return ""

    def parse_html_with_bs4(self, html_content: str) -> List[Dict]:
        """Парсит HTML с помощью BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Находим все элементы работ
            work_elements = soup.select("li.work.blurb.group")
            self.logger.info(f"📚 Найдено {len(work_elements)} элементов работ")

            works = []
            for i, work_element in enumerate(work_elements, 1):
                try:
                    work_data = self.parse_work_element_bs4(work_element)
                    if (
                        work_data
                        and work_data.get("title")
                        and work_data.get("title") != "Неизвестно"
                    ):
                        works.append(work_data)
                        self.logger.info(
                            f"✅ Работа {i}: {work_data.get('title', 'Неизвестно')}"
                        )
                    else:
                        self.logger.warning(f"⚠️ Работа {i}: не удалось извлечь данные")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка при парсинге работы {i}: {e}")
                    continue

            return works

        except Exception as e:
            self.logger.error(f"❌ Ошибка парсинга HTML: {e}")
            return []

    def parse_work_element_bs4(self, work_element) -> Dict:
        """Парсит элемент работы с помощью BeautifulSoup"""
        import re

        try:
            work_data = {}

            # 1. Заголовок и URL
            title = ""
            url = ""
            work_id = None

            try:
                # Ищем заголовок разными способами
                title_selectors = [
                    "h4.heading a",
                    ".heading a",
                    "h4 a",
                    "a[href*='/works/']",
                ]

                for selector in title_selectors:
                    try:
                        title_link = work_element.select_one(selector)
                        if title_link and title_link.text.strip():
                            title = title_link.text.strip()
                            href = title_link.get("href", "")

                            # Исправляем URL
                            if href.startswith("http"):
                                url = href
                            else:
                                url = "https://archiveofourown.gay" + href

                            # Извлекаем ID работы
                            work_id_match = re.search(r"/works/(\d+)", url)
                            if work_id_match:
                                work_id = work_id_match.group(1)
                            break
                    except:
                        continue

                if not title:
                    # Если не нашли через селекторы, попробуем найти по href
                    all_links = work_element.select("a[href*='/works/']")
                    if all_links:
                        title_link = all_links[0]
                        title = title_link.text.strip()
                        href = title_link.get("href", "")
                        if href.startswith("http"):
                            url = href
                        else:
                            url = "https://archiveofourown.gay" + href
                        work_id_match = re.search(r"/works/(\d+)", url)
                        if work_id_match:
                            work_id = work_id_match.group(1)

            except Exception as e:
                self.logger.error(f"❌ Ошибка парсинга заголовка: {e}")

            work_data["title"] = title or "Неизвестно"
            work_data["url"] = url or ""
            work_data["work_id"] = work_id

            # 2. Автор
            author_text = "Неизвестен"
            try:
                heading = work_element.select_one("h4.heading")
                if heading:
                    heading_text = heading.text
                    if "by" in heading_text:
                        author_part = heading_text.split("by", 1)[1].strip()
                        author_text = re.sub(r"\s+", " ", author_part).strip()
                        if not author_text or author_text == "Anonymous":
                            author_text = "Anonymous"
            except:
                pass

            work_data["author"] = author_text

            # 3. Фандомы
            fandoms = []
            try:
                fandom_links = work_element.select("h5.fandoms a.tag")
                fandoms = [link.text.strip() for link in fandom_links]
            except:
                pass

            # Фильтруем дублирующиеся фандомы
            fandoms = list(
                dict.fromkeys(fandoms)
            )  # Убираем дубликаты, сохраняя порядок
            work_data["fandoms"] = fandoms

            # 4. Теги (разделяем на категории)
            all_tags = []
            warnings = []
            relationships = []
            tags = []

            try:
                tag_links = work_element.select("ul.tags.commas a.tag")
                all_tags = [link.text.strip() for link in tag_links]
                self.logger.debug(f"Найдено тегов: {len(all_tags)}")
                self.logger.debug(f"Теги: {all_tags[:5]}...")  # Показываем первые 5

                # Разделяем теги по категориям
                for tag in all_tags:
                    if tag in Config.WARNING_TAGS:
                        warnings.append(tag)
                    elif "/" in tag and all(
                        [
                            exception_item not in tag
                            for exception_item in Config.RELATIONSHIP_EXCEPTIONS
                        ]
                    ):
                        relationships.append(tag)
                    else:
                        tags.append(tag)

                self.logger.debug(
                    f"Результат разделения - warnings: {len(warnings)}, relationships: {len(relationships)}, tags: {len(tags)}"
                )

            except Exception as e:
                self.logger.error(f"Ошибка при парсинге тегов: {e}")
                pass

            work_data["warnings"] = warnings
            work_data["relationships"] = relationships
            work_data["tags"] = tags

            # 5. Рейтинг
            rating = ""
            try:
                rating_element = work_element.select_one("ul.required-tags .rating")
                if rating_element:
                    rating = rating_element.get("title") or rating_element.text.strip()
            except:
                pass
            work_data["rating"] = rating

            # 6. Статистика
            stats = {}
            try:
                stats_section = work_element.select_one("dl.stats")
                if stats_section:
                    # Слова
                    try:
                        words_element = stats_section.select_one("dd.words")
                        stats["words"] = (
                            words_element.text.strip() if words_element else "0"
                        )
                    except:
                        stats["words"] = "0"

                    # Главы
                    try:
                        chapters_element = stats_section.select_one("dd.chapters")
                        stats["chapters"] = (
                            chapters_element.text.strip() if chapters_element else "1/1"
                        )
                    except:
                        stats["chapters"] = "1/1"

                    # Язык
                    try:
                        language_element = stats_section.select_one("dd.language")
                        stats["language"] = (
                            language_element.text.strip()
                            if language_element
                            else "Unknown"
                        )
                    except:
                        stats["language"] = "Unknown"

                    # Kudos
                    try:
                        kudos_element = stats_section.select_one("dd.kudos")
                        stats["kudos"] = (
                            kudos_element.text.strip() if kudos_element else "0"
                        )
                    except:
                        stats["kudos"] = "0"

                    # Комментарии
                    try:
                        comments_element = stats_section.select_one("dd.comments")
                        stats["comments"] = (
                            comments_element.text.strip() if comments_element else "0"
                        )
                    except:
                        stats["comments"] = "0"

                    # Закладки
                    try:
                        bookmarks_element = stats_section.select_one("dd.bookmarks")
                        stats["bookmarks"] = (
                            bookmarks_element.text.strip() if bookmarks_element else "0"
                        )
                    except:
                        stats["bookmarks"] = "0"
                else:
                    stats = {
                        "words": "0",
                        "chapters": "1/1",
                        "language": "Unknown",
                        "kudos": "0",
                        "comments": "0",
                        "bookmarks": "0",
                    }
            except Exception as e:
                self.logger.warning(f"⚠️ Секция статистики не найдена: {e}")
                stats = {
                    "words": "0",
                    "chapters": "1/1",
                    "language": "Unknown",
                    "kudos": "0",
                    "comments": "0",
                    "bookmarks": "0",
                }

            work_data["stats"] = stats

            # 7. Дата обновления
            try:
                date_element = work_element.select_one("p.datetime")
                work_data["updated_at"] = (
                    date_element.text.strip() if date_element else "Unknown"
                )
            except:
                work_data["updated_at"] = "Unknown"

            # 8. Краткое описание
            try:
                summary_element = work_element.select_one(
                    "blockquote.userstuff.summary"
                )
                work_data["summary"] = (
                    summary_element.text.strip() if summary_element else ""
                )
            except:
                work_data["summary"] = ""

            return work_data

        except Exception as e:
            self.logger.error(f"❌ Ошибка при парсинге работы: {e}")
            return {
                "title": "Неизвестно",
                "url": "",
                "work_id": None,
                "author": "Неизвестен",
                "fandoms": [],
                "tags": [],
                "rating": "",
                "stats": {
                    "words": "0",
                    "chapters": "1/1",
                    "language": "Unknown",
                    "kudos": "0",
                    "comments": "0",
                    "bookmarks": "0",
                },
                "updated_at": "Unknown",
                "summary": "",
            }

    def save_results(self, works: List[Dict], filename: str):
        """Сохраняет результаты в JSON файл"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(works, f, ensure_ascii=False, indent=2)
            self.logger.info(f"📄 Результаты сохранены в {filename}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения результатов: {e}")

    def run_crawler(
        self,
        fandoms: List[str] = None,
        max_works: int = None,
    ) -> List[Dict]:
        """Основной метод запуска краулера"""
        try:
            self.logger.info("🚀 Запуск улучшенного краулера AO3...")

            # Настраиваем драйвер
            if not self.setup_driver():
                return []

            # Пытаемся загрузить куки, если не получается - логинимся
            if self.username and self.password:
                if not self.load_cookies():
                    self.logger.info(
                        "🔄 Куки не найдены или недействительны, логинимся..."
                    )
                    if not self.login():
                        self.logger.error("❌ Не удалось войти в систему")
                        return []
            else:
                self.logger.info("⚠️ Работаем без входа в систему")

            # Используем фандомы из конфига по умолчанию
            if fandoms is None:
                fandoms = Config.SEARCH_FANDOMS

            # Используем максимальное количество работ из конфига
            if max_works is None:
                max_works = Config.MAX_WORKS_PER_RUN

            # Получаем HTML
            html_content = self.get_search_html(fandoms=fandoms)
            if not html_content:
                return []

            # Парсим HTML
            works = self.parse_html_with_bs4(html_content)

            # Ограничиваем количество работ
            if max_works and len(works) > max_works:
                works = works[:max_works]

            self.logger.info(f"📚 Найдено {len(works)} работ")

            # Сохраняем результаты
            if works:
                filename = "improved_search.json"
                self.save_results(works, filename)

            return works

        except Exception as e:
            self.logger.error(f"❌ Ошибка в run_crawler: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

    def __del__(self):
        if self.driver:
            self.driver.quit()


def main():
    """Основная функция для тестирования"""
    print("🧪 Тестирование улучшенного краулера AO3...")

    # Создаем краулер
    crawler = ImprovedCrawler()

    # Ищем работы по фандомам из конфига
    print(f"\n1. Ищу работы по фандомам: {Config.SEARCH_FANDOMS}")
    works = crawler.run_crawler()

    if works:
        print(f"✅ Найдено {len(works)} работ")

        # Выводим информацию
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ПОИСКА:")
        print("=" * 60)

        for i, work in enumerate(works, 1):
            print(f"\n{i}. {work['title']}")
            print(f"   Автор: {work['author']}")
            print(f"   URL: {work['url']}")
            if work["tags"]:
                print(f"   Теги: {', '.join(work['tags'][:5])}...")
            if work["fandoms"]:
                print(f"   Фандомы: {', '.join(work['fandoms'])}")
            if work["rating"]:
                print(f"   Рейтинг: {work['rating']}")
            if work["stats"]:
                print(f"   Статистика: {work['stats']}")
            if work["summary"]:
                print(f"   Описание: {work['summary'][:100]}...")
    else:
        print("❌ Работ не найдено")


if __name__ == "__main__":
    main()
