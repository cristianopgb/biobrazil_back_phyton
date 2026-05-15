def success_response(data: dict, message: str = "ok") -> dict:
    return {"message": message, "data": data}
