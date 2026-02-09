
class BallChasingClientError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class BallChasingAuthError(BallChasingClientError):
    def __init__(self, message: str):
        super().__init__(message)

class BallChasingRequestError(BallChasingClientError):
    def __init__(self, message: str):
        super().__init__(message)

class BallChasingServerError(BallChasingClientError):
    def __init__(self, message: str):
        super().__init__(message)

class BallChasingUnexpectedError(BallChasingClientError):
    def __init__(self, message: str):
        super().__init__(message)
