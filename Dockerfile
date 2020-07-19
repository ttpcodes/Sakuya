FROM python:3.8.4-alpine3.12

RUN apk add --no-cache --virtual build gcc g++ linux-headers musl-dev postgresql-dev

COPY . /srv
WORKDIR /srv
RUN pip install -r requirements.txt

RUN apk del build
RUN apk add --no-cache libpq libstdc++

CMD ["python", "-m", "sakuya"]
