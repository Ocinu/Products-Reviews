FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app

ENV PYTHONPATH="/app"

RUN ruff check .
RUN pylint ./core

CMD ["python", "core/app.py"]
