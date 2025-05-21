FROM ubuntu:jammy-20240227

ARG BASE_DIR=/app

ENV \
    DEBIAN_FRONTEND=noninteractive \
    \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # poetry
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        pipx \
        git \
        \
        # Install following python packages via system package manager instead of Poetry
        # to avoid complex and buggy compilation process
        python3-pil \
        python3-psycopg2 \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists

RUN PIPX_BIN_DIR=/usr/local/bin pipx install poetry==1.8.2

WORKDIR ${BASE_DIR}

COPY pyproject.toml ./poetry.lock ./

RUN poetry install -v --no-ansi

RUN mkdir -p \
    /root/postgresql/ \
    /var/www/collected_static \
    /var/www/media/

COPY src src

ENV PORT=80
EXPOSE 80/tcp

RUN ln -sf /usr/bin/python3 /usr/bin/python
WORKDIR ${BASE_DIR}/src

RUN SITE_ROOT_URL='http://127.0.0.1:8000' \
    POSTGRES_DSN='postgres://notexist:notexist@notexist:5432/notexist' \
    DJ_SECRET_KEY='empty' \
    REDIS_RQ_DSN='redis://notexist:6379/0' \
    ./manage.py collectstatic

CMD gunicorn todo_list.wsgi:application --access-logfile -
