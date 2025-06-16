from satellitevu.http.base import ResponseWrapper


class AuthError(RuntimeError):
    def __init__(
        self,
        message: str,
        response: ResponseWrapper | None = None,
        request_args: list = [],
        request_kwargs: dict = {},
    ):
        super().__init__(message)
        self.response = response
        self.request_args = request_args
        self.request_kwargs = request_kwargs


class Api401Error(AuthError):
    pass


class Api403Error(AuthError):
    pass
