FROM python:3.7

RUN mkdir -p /code/dataset-explorer
RUN mkdir /code/dataset-explorer/data
WORKDIR /code/dataset-explorer
VOLUME /code/dataset-explorer/data

RUN pip install poetry==1.1.1
COPY pyproject.toml poetry.lock /code/dataset-explorer/
RUN poetry export --without-hashes -f requirements.txt > reqs.txt \
    && pip install -r reqs.txt

COPY . /code/dataset-explorer
CMD ["uvicorn", "--port", "8000", "--host", "0.0.0.0", "explorer.web:app"]
