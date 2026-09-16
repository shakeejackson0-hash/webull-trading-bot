"""Configuration loader for the Webull trading bot."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_KEY: str = os.getenv("WEBULL_APP_KEY", "")
    APP_SECRET: str = os.getenv("WEBULL_APP_SECRET", "")
    REGION: str = os.getenv("WEBULL_REGION", "us")
    ENDPOINT: str = os.getenv("WEBULL_ENDPOINT", "api.sandbox.webull.com")
    ACCOUNT_ID: str = os.getenv("WEBULL_ACCOUNT_ID", "")
    DEFAULT_SYMBOL: str = os.getenv("DEFAULT_SYMBOL", "AAPL")

    @classmethod
    def validate(cls) -> None:
        if not cls.APP_KEY or not cls.APP_SECRET:
            raise ValueError(
                "WEBULL_APP_KEY and WEBULL_APP_SECRET must be set in .env"
            )
