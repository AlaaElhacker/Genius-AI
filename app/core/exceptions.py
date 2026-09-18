class AppError(Exception):
    """Base application error with a user-safe message."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class DuplicateError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class ServiceError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class QuotaError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=429)
