# Weather Telegram Bot

Этот проект представляет собой Telegram-бота для получения прогноза погоды. Бот использует API OpenWeatherMap для получения данных о погоде и SQLite для хранения данных геолокации пользователей. Проект разворачивается в Docker контейнерах и использует Docker Compose для управления многоконтейнерными приложениями.

## Установка и запуск

### Предварительные требования

- Docker
- Docker Compose

### Настройка

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/dagrishin/weather_bot.git
    cd weather_bot
    ```

2. Создайте файл `.env` и добавьте в него ваш Telegram Bot API Token и API ключ OpenWeatherMap:

    ```sh
    TELEGRAM_API_TOKEN=your_telegram_bot_api_token
    OPENWEATHER_API_KEY=your_openweather_api_key
    ```

### Сборка и запуск

Постройте и запустите контейнеры:

    ```sh
    docker-compose up --build
    ```

## Использование

Бот поддерживает следующие команды:

- `/start` - Начать взаимодействие с ботом
- `/help` - Получить список доступных команд
- `/add_location` - Добавить геолокацию
- `/locations` - Показать сохраненные геолокации
- `/delete` - Удалить геолокацию
- `/cancel` - Отменить текущее действие

## Функции

### bot/handlers.py

- Регистрация команд и их обработчиков.
- Обработка сообщений от пользователя.

### bot/keyboards.py

- Создание клавиатур для взаимодействия с пользователем.

### bot/states.py

- Определение состояний для FSM.

### bot/weather.py

- Получение данных о погоде от OpenWeatherMap API.

### database/db.py

- Создание и управление базой данных SQLite.

## Dockerfile

Описывает процесс сборки Docker-образа для Python приложения.

## docker-compose.yml

Управляет многоконтейнерным приложением. Содержит конфигурацию для контейнеров `bot`.

### Автоперезапуск

Контейнеры настроены на автоматический перезапуск в случае падения:

```yaml
services:
  bot:
    restart: always
Требования
Список зависимостей проекта находится в requirements.txt.

Лицензия
Этот проект лицензирован под MIT License. Подробности см. в файле LICENSE.


Эти инструкции помогут вам установить, настроить и запустить Telegram-бота для прогноза погоды.