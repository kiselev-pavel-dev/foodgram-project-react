FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

RUN apt update && apt -y install libpq-dev build-essential

RUN python -m pip install --upgrade pip

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
