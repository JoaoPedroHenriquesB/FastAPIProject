class TaskNotFoundError(Exception):
    """Task not found in database"""
    pass

class PermissionDeniedError(Exception):
    """this user is not allowed to perform this action"""
    pass
