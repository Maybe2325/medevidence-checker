FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml package.json LICENSE README.md ./
COPY .kiro ./.kiro
COPY packages ./packages
COPY apps ./apps
COPY benchmarks ./benchmarks
COPY tests ./tests

RUN pip install --no-cache-dir fastapi uvicorn pydantic hypothesis pytest httpx pyyaml

EXPOSE 8000

CMD ["uvicorn", "apps.backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
