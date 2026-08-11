import os
import secrets
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.errors import ApiError, error_payload
from app.models import Product, ProductList
from app.repository import ProductRepository

REQUEST_ID_HEADER = "X-Request-ID"
SERVICE_VERSION = os.getenv("APP_VERSION", "").strip() or "1.0.0"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or secrets.token_hex(8)
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


app = FastAPI(
    title="NexusCart Catalog Service",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url=None,
)
app.add_middleware(RequestIdMiddleware)

repository = ProductRepository()


def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content=error_payload(error.code, error.message, request_id(request)),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_payload(
            "VALIDATION_ERROR", "Request validation failed", request_id(request)
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    request: Request, error: StarletteHTTPException
) -> JSONResponse:
    code = "ROUTE_NOT_FOUND" if error.status_code == 404 else "HTTP_ERROR"
    message = "Route does not exist" if error.status_code == 404 else str(error.detail)
    return JSONResponse(
        status_code=error.status_code,
        content=error_payload(code, message, request_id(request)),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "UP",
        "service": "catalog-service",
        "version": SERVICE_VERSION,
    }


@app.get("/api/v1/products", response_model=ProductList)
async def list_products() -> ProductList:
    return ProductList(items=repository.find_all())


@app.get("/api/v1/products/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    product = repository.find_by_id(product_id)
    if product is None:
        raise ApiError(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message=f"Product {product_id} does not exist",
        )
    return product
