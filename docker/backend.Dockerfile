FROM python:3.11-bookworm AS deps

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-bookworm AS runtime

WORKDIR /app

COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]