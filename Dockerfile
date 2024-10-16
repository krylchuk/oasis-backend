FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pipenv install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app"]
