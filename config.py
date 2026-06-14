import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: str

    @classmethod
    def load(cls) -> "Config":
        def required(key: str) -> str:
            value = os.getenv(key)
            if not value:
                raise RuntimeError(f"Missing required env var: {key}")
            return value

        return cls(
            bot_token=required("BOT_TOKEN"),
            db_host=required("DB_HOST"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=required("DB_NAME"),
            db_user=required("DB_USER"),
            db_pass=required("DB_PASS"),
        )

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
