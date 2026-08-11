from dataclasses import dataclass


@dataclass(slots=True)
class ApiError(Exception):
    status_code: int
    code: str
    message: str


def error_payload(code: str, message: str, request_id: str) -> dict[str, object]:
    return {
        "error": {
            "code": code,
            "message": message,
            "requestId": request_id,
        }
    }
