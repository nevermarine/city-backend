FROM python:3.11-slim

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml ./
ADD src/ ./
RUN touch README.md

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

ENTRYPOINT ["poetry", "run", "python", "-m", "main"]
