def ResponseModel(data, code: int, message: str):
    return {
        "data": data,
        "statusCode": code,
        "message": message,
    }


def ErrorResponseModel(code: int, message: str):
    return {
        "statusCode": code,
        "message": message,
    }
