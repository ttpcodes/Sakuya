FROM python:3.8.1-alpine3.11

RUN apk add --no-cache --virtual build gcc musl-dev postgresql-dev

COPY . /srv
WORKDIR /srv
RUN pip install -r requirements.txt

RUN apk del build
RUN apk add --no-cache libpq

CMD ["python", "-m", "sakuya"]
