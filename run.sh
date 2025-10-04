#!/bin/bash

# Скрипт для запуска AO3 Crawler

echo "🚀 Запуск AO3 Crawler..."

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте env_example.txt в .env и заполните переменные:"
    echo "cp env_example.txt .env"
    echo "nano .env"
    exit 1
fi

# Проверяем установку uv
if ! command -v uv &> /dev/null; then
    echo "📦 Устанавливаю uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "🔧 Создаю виртуальное окружение с uv..."
uv venv

echo "📥 Устанавливаю зависимости с uv..."
uv pip install -r requirements.txt

echo "🕷️ Запускаю краулер..."
uv run python main.py "$@"
