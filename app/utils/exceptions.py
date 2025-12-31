class NotFoundError(Exception):
    """raise when a task is not found in database"""

    pass


class PermissionDeniedError(Exception):
    """raised when an user is not allowed to perform an action"""

    pass


class UserNotFoundError(Exception):
    """raised when a user is not found in database"""


class DuplicateEntityError(Exception):
    """raised when attempting to create an entity that violates de uniqueness constraint"""

    def __init__(self, field: str | None = None, message: str | None = None) -> None:
        super().__init__(message or "duplicate entity")
        self.field = field
        self.message = message or "duplicate entity"


class InternalDomainError(Exception):
    """generic domain-level internal error"""
