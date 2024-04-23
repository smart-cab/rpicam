FROM python:slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.6.1

WORKDIR /app

RUN apt-get update && apt-get install -y git libglib2.0-0 libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock README.md .
RUN poetry config --no-cache virtualenvs.create false && poetry install --no-cache --no-root --no-interaction --no-ansi --only main

COPY . .
RUN poetry install --no-cache --no-interaction --no-ansi --only main

RUN git clone --depth=1 https://github.com/smart-cab/certs.git /app/certs

CMD ["poetry", "run", "python", "rpicam"]
EXPOSE 5050
