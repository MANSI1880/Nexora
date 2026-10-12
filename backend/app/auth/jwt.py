import os
from datetime import datetime, timedelta, timezone
from jose import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

def get_jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "change-me")

def validate_jwt_secret(secret: str | None = None, environment: str | None = None) -> bool:
    sec = secret if secret is not None else get_jwt_secret()
    env = (environment if environment is not None else os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development"))).lower()

    if env in ["production", "prod"]:
        if not sec or sec == "change-me":
            raise ValueError("JWT_SECRET must be set to a secure secret in production; default 'change-me' is not allowed.")
    return True

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_jwt_secret(), algorithm=JWT_ALGORITHM)
    return encoded_jwt
