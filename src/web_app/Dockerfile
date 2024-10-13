FROM python:3.12-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.3

RUN pip install poetry

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --only=main --no-ansi

WORKDIR /code

COPY src/web_app/* /code/app/

CMD ["fastapi", "run", "app/main.py", "--port", "5050"]