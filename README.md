# city-backend
Бекенд для горолда Зарафшан.

## Как билдить и запускать
Для сборки требуется poetry.
```bash
git clone https://github.com/nevermarine/city-backend
cd city-backend
poetry install
poetry shell
uvicorn main:app --reload
```
Swagger будет доступен по адресу http://localhost:8000/docs.
