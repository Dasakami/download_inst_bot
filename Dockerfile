
FROM python:3.12-slim


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/sessions

EXPOSE 8000


ENV SESSION=/app/sessions/dskenglish.dsk.session


CMD ["python", "bot/main.py"]
