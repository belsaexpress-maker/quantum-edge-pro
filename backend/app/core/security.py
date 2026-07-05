def create_access_token(data: dict):
    return "dev-token"


def get_current_user_payload():
    return {
        "sub": "1",
        "email": "belsaexpress@gmail.com",
        "role": "admin",
    }


def get_current_user():
    return get_current_user_payload()


def require_bot_access():
    return get_current_user_payload()


def require_admin():
    return get_current_user_payload()