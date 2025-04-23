import orjson

from typing import Optional


class SSEResponseModel:
    def __init__(
        self,
        status: str,
        message: str,
        code: int,
        data: Optional[dict] = None,
    ):
        self.statusCode = code
        self.status = status
        self.message = message
        self.data = data

    def to_dict(self) -> dict:
        data = {
            "statusCode": self.statusCode,
            "status": self.status,
            "message": self.message,
            "data": self.data,
        }
        return data

    def to_json(self) -> str:
        return orjson.dumps(self.to_dict()).decode("utf-8")

    def to_sse(self) -> str:
        return f"data: {self.to_json()}\n\n"
