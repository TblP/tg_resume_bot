# Telegram Resume Bot

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?style=flat&logo=telegram&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat&logo=openai&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-API-FF9D00?style=flat&logo=huggingface&logoColor=white)

Бот для Telegram, который генерирует резюме из текста или PDF-файлов, фильтрует мусорные сообщения и конвертирует результаты в PDF с использованием модели `xlm-roberta-base`.

## Описание

- Генерация резюме из текстовых сообщений Telegram.
- Извлечение текста из PDF и создание суммированного резюме без лишней информации.
- Классификация сообщений с помощью модели `xlm-roberta-base`.

## Структура проекта

```
tg_resume_bot/
├── Fonts/                      # Шрифты (bg.png, Roboto-Bold.ttf, Roboto-Regular.ttf)
├── .env                        # Переменные окружения
├── .gitignore                  # Файл игнорирования Git
├── convert_to_pdf.py           # Конвертация в PDF
├── main.py                     # Основной скрипт бота
├── openai_api.py               # Интеграция с OpenAI API
├── parse_pdf.py                # Парсинг PDF
├── run_model.py                # Скрипт запуска модели
├── README.md                   # Документация
├── requirements.txt            # Зависимости
```

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/TblP/tg_resume_bot.git
   cd tg_resume_bot
   ```

2. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # На Windows: .venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте `.env`:
   ```env
   TELEGRAM_TOKEN=ваш_токен_бота
   OPENAI_API_KEY=ваш_ключ_openai 
   ```

## Использование

1. Запустите бота:
   ```bash
   python main.py
   ```

2. Взаимодействие:
   - Отправьте текст/PDF для создания резюме тг боту. 
   - Бот фильтрует спам с помощью модели.
   - Возвращает PDF переработанное резюме

## Требования

- Python 3.11+
- Telegram Bot API
- ключ OpenAI API 
