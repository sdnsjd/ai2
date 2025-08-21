FROM python:3.11.5-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY requirements.txt .


RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY . .

CMD ["python", "main.py"]