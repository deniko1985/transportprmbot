FROM python:3.10.6-alpine

WORKDIR /bot_app
#ENTRYPOINT ["./docker-entrypoint.sh"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3001

#ENV APP_VERSION=1.0
#ENV APP_NAME=transportprmbot

CMD [ "python", "main.py", "--host", "127.0.0.1", "--port", "3001"]

