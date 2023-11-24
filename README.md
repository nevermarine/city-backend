# city-backend
Бекенд для горолда Зарафшан.

## Как билдить (без Docker)
Для сборки требуется poetry.
```bash
git clone https://github.com/nevermarine/city-backend
cd city-backend
poetry install
poetry shell
uvicorn main:app --reload
```
## Как билдить (с Docker)
```bash
git clone https://github.com/nevermarine/city-backend
cd city-backend
docker compose up
```

Swagger будет доступен по адресу http://localhost:5000/docs.
