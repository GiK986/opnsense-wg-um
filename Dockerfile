FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN apk add --update --no-cache wireguard-tools openssl&& \
    pip install --upgrade pip && pip install -r requirements.txt

RUN openssl rand -hex 32 >> /app/secret_key.txt

COPY . /app/

EXPOSE 8000

RUN chmod +x /app/startup.sh

CMD ["/bin/sh","-c","./startup.sh"]

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]