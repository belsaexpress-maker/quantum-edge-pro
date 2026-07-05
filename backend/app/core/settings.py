from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Quantum Edge Ultimate"
    VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./quantum_edge_ultimate.db"

    SECRET_KEY: str = "quantum-edge-ultimate-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]


settings = Settings()