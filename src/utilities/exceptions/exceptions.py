from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "User already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
