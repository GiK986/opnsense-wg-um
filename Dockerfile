FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN apk add --update --no-cache wireguard-tools && \
    pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]