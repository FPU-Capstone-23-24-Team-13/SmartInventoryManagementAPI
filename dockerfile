
# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /app 

COPY ./requirements.txt /app 
RUN pip install --upgrade pip
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000
ENV FLASK_APP=app.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
