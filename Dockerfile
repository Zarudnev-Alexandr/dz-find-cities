FROM python:3.10-slim

WORKDIR /

RUN apt-get update && apt-get install -y iputils-ping

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads && chmod -R 755 /app/uploads

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]