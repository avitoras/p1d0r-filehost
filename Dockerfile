FROM python:3.9-alpine3.20

WORKDIR /app

RUN apk update && apk add --no-cache build-base python3-dev libffi-dev openssl-dev

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]