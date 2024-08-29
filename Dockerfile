FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 5000

CMD ["python", "main.py"]