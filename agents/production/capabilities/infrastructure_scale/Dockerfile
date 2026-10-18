FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir "fastapi>=0.115,<1" "uvicorn>=0.30,<1"

COPY agents/production/capabilities/__init__.py /app/agents/production/capabilities/__init__.py
COPY agents/production/capabilities/user_experience_application /app/agents/production/capabilities/user_experience_application

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "agents.production.capabilities.user_experience_application.main:app", "--host", "0.0.0.0", "--port", "8000"]
