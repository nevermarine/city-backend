# hadolint global ignore=DL3020
FROM python:3.11-slim

RUN pip install --no-cache-dir poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml ./
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

COPY .env ./
ADD src/ ./src
RUN touch README.md

ENTRYPOINT ["poetry", "run", "python", "-m", "src.main"]
