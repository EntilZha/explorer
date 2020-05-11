FROM python:3.8

RUN pip install poetry
RUN mkdir /app
WORKDIR /app
VOLUME /app/data

COPY pyproject.toml poetry.lock /app/
RUN poetry install

EXPOSE 80

COPY . /app

CMD ["poetry", "run", "uvicorn", "qanta.web:app", "--host", "0.0.0.0", "--port", "80"]