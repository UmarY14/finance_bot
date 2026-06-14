import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_url: str | None
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

        bot_token = required("BOT_TOKEN")

        # Managed hosts (Railway/Render) expose a single DATABASE_URL. If present,
        # it takes precedence and the discrete DB_* vars are not required.
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return cls(
                bot_token=bot_token,
                database_url=database_url,
                db_host="",
                db_port=5432,
                db_name="",
                db_user="",
                db_pass="",
            )

        return cls(
            bot_token=bot_token,
            database_url=None,
            db_host=required("DB_HOST"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=required("DB_NAME"),
            db_user=required("DB_USER"),
            db_pass=required("DB_PASS"),
        )

    @property
    def dsn(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
