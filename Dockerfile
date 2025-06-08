FROM python:3.12-alpine

RUN pip install poetry
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /bot
COPY ./ ./
RUN poetry install --no-interaction --no-ansi

CMD poetry run bot