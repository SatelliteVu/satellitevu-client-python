class AuthError(RuntimeError):
    pass


class Api401Error(AuthError):
    pass


class Api403Error(AuthError):
    pass
