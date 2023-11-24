# city-backend
Бэкенд для сайта г.Зарафшан. Основан на ```fastapi```.

# Build
## Локально
Для сборки требуется poetry.

```bash
git clone https://github.com/nevermarine/city-backend
cd city-backend
poetry install
poetry shell
python3 -m src.main
```
Для модуля ```src.main``` можно задать различные аргументы. Например, ```port``` и ```host```. Посмотреть все аргументы можно с помощью ```python3 -m src.main --help```

## Docker compose
Для запуска docker контейнера необходимо выполнить следующие шаги:
```bash
git clone https://github.com/nevermarine/city-backend
cd city-backend
docker compose up
```

Swagger будет доступен по адресу http://localhost:5000/docs.

# For contributors
## Структура
Весь код для бэкенда находится в папке ```src```.

Модели (иначе говоря типы) должны располагаться в папке ```model``` и использовать библиотеку ```pydantic```. Функции должны быть аннотированы.

Код для авторизации находится в папке auth.

## Название веток
Названия веток должны быть минимальны, не более 3 слов. Слова должны разделяться дефисом и начинаться с маленькой буквы. Например: ```base-models, test-auth, sign-in```.

## PR
Обязательно описание PR. Только после прохождения всех тестов PR будет рассмотрен модераторами. Также необходимо установить ```pre-commit```, он уже состоит в ```pyproject.toml```. При каждом коммите он будет запускаться.
