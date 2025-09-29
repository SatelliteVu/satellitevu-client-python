from typing import Any


class ApiError(RuntimeError):
    def __init__(self, *args: Any, response_status: str, response_text: str):
        super().__init__(*args)
        self.response_status = response_status
        self.response_text = response_text

class AuthError(RuntimeError):
    pass


class Api401Error(ApiError, AuthError):
    def __init__(self, *args: Any, response_text: str):
        super().__init__(*args, response_status=401, response_text=response_text)


class Api403Error(ApiError, AuthError):
    def __init__(self, *args: Any, response_text: str):
        super().__init__(*args, response_status=403, response_text=response_text)


class ApiClientError(ApiError):
    pass


class ApiServerError(ApiError):
    pass