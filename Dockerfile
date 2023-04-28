FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN apk add --update --no-cache wireguard-tools openssl&& \
    pip install --upgrade pip && pip install -r requirements.txt

RUN openssl rand -hex 32 >> /app/secret_key.txt

ENV CSRF_TRUSTED_ORIGINS="http://localhost;http://127.0.0.1"
ENV ALLOWED_HOSTS="127.0.0.1;localhost"
ENV DEBUG="False"

# Email settings
ENV EMAIL_HOST="smtp.gmail.com"
ENV EMAIL_PORT="587"
ENV EMAIL_HOST_USER=""
ENV EMAIL_HOST_PASSWORD=""
ENV DEFAULT_FROM_EMAIL=""
ENV EMAIL_USE_TLS="True"
ENV EMAIL_USE_SSL="False"

COPY . /app/

EXPOSE 8000

RUN chmod +x /app/startup.sh

CMD ["/bin/sh","-c","./startup.sh"]
