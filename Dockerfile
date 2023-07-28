# pull official base image
FROM python:3.11-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add --update --no-cache wireguard-tools postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./src/requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./src/config/entrypoint.sh ./config/entrypoint.sh
RUN sed -i 's/\r$//g' /usr/src/app/config/entrypoint.sh
RUN chmod +x /usr/src/app/config/entrypoint.sh

# copy project
COPY ./src .

# run entrypoint.sh
ENTRYPOINT ["./config/entrypoint.sh"]
