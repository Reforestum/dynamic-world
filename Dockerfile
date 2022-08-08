FROM python:3.9.13 as base

ENV POETRY_VERSION=1.1.14 \
  PATH="/root/.local/bin:$PATH"

# Install poetry: # https://python-poetry.org/docs/master/#installation
RUN apt-get update && \
  apt-get install -y curl && \
  curl -sSL https://install.python-poetry.org | python3 - --version "$POETRY_VERSION" && \
  poetry config virtualenvs.create false

# Install gdal
RUN apt-get install -y binutils libproj-dev gdal-bin

#############################################
FROM base as dev

WORKDIR /app
COPY  poetry.lock pyproject.toml ./
RUN poetry install --no-interaction
COPY . /app

#############################################
FROM base as prod

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --only main
COPY . /app
CMD [ "python", "main.py" ]
