from fastapi.testclient import TestClient

from app.main import SERVICE_IMAGE_TAG, SERVICE_VERSION, app


client = TestClient(app)


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


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "UP",
        "service": "catalog-service",
        "version": SERVICE_VERSION,
        "imageTag": SERVICE_IMAGE_TAG,
    }
