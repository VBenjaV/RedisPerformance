from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://shopnow:shopnow@localhost:5432/shopnow"
    redis_url: str = "redis://localhost:6379/0"
    simulated_db_latency_ms: int = 350
    cache_ttl_seconds: int = 120
    cache_enabled: bool = True
    payment_simulation_ms: int = 50
    orders_channel: str = "shopnow:orders"
    events_list_key: str = "shopnow:events"
    events_list_max: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
