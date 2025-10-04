#!/bin/bash

# Скрипт для быстрой установки AO3 Crawler с uv

echo "🚀 Установка AO3 Crawler..."

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "📝 Создаю файл конфигурации..."
    cp env_example.txt .env
    echo "⚠️  Не забудьте отредактировать .env файл с вашими данными!"
fi

# Устанавливаем uv если не установлен
if ! command -v uv &> /dev/null; then
    echo "📦 Устанавливаю uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✅ uv установлен"
else
    echo "✅ uv уже установлен"
fi

# Создаем виртуальное окружение
echo "🔧 Создаю виртуальное окружение..."
uv venv

# Устанавливаем зависимости
echo "📥 Устанавливаю зависимости..."
uv pip install -r requirements.txt

echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте .env файл с вашими данными:"
echo "   nano .env"
echo ""
echo "2. Запустите краулер:"
echo "   ./run.sh"
echo ""
echo "3. Или в непрерывном режиме:"
echo "   ./run.sh --continuous"
