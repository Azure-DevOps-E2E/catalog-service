import asyncio
import json

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.main import (
    SERVICE_IMAGE_TAG,
    SERVICE_VERSION,
    app,
    validation_error_handler,
)


client = TestClient(app)


def _make_request(path: str = "/") -> Request:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 123),
        "server": ("testserver", 80),
        "root_path": "",
    }
    return Request(scope)


def test_list_products_returns_seed_data_and_request_id() -> None:
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 5
    assert response.headers["X-Request-ID"]


def test_get_product_propagates_request_id() -> None:
    response = client.get(
        "/api/v1/products/prd-001", headers={"X-Request-ID": "catalog-test"}
    )

    assert response.status_code == 200
    assert response.json()["price"] == 1_290_000
    assert response.headers["X-Request-ID"] == "catalog-test"


def test_missing_product_uses_common_error_shape() -> None:
    response = client.get(
        "/api/v1/products/prd-999", headers={"X-Request-ID": "missing-test"}
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "PRODUCT_NOT_FOUND",
            "message": "Product prd-999 does not exist",
            "requestId": "missing-test",
        }
    }


def test_missing_route_uses_common_error_shape() -> None:
    response = client.get("/does-not-exist", headers={"X-Request-ID": "route-test"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "ROUTE_NOT_FOUND",
            "message": "Route does not exist",
            "requestId": "route-test",
        }
    }


def test_validation_error_handler_uses_request_id() -> None:
    async def run() -> None:
        request = _make_request()
        request.state.request_id = "validation-test"

        response = await validation_error_handler(request, RequestValidationError([]))

        assert response.status_code == 422
        assert json.loads(response.body) == {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "requestId": "validation-test",
            }
        }

    asyncio.run(run())


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "UP",
        "service": "catalog-service",
        "version": SERVICE_VERSION,
        "imageTag": SERVICE_IMAGE_TAG,
    }