# Catalog Service

Python + FastAPI service that owns product descriptions, prices and current stock.

## API

- `GET /health`
- `GET /api/v1/products`
- `GET /api/v1/products/{id}`
- `GET /docs` for the private OpenAPI UI

`GET /health` returns `status`, `service` and the deployed `version`.
Set `APP_VERSION` at runtime; it defaults to `1.0.0` for local runs.

## Run and test

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --port 8000
pytest
```

## Container

```bash
docker build -t catalog-service .
```
