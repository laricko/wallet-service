from environs import Env

env = Env()
env.read_env()


class Config:
    DEBUG: bool
    HOST: str = env("HOST")
    PORT: int = env("PORT")
    DATABASE_URI: str = f"postgresql://{env('POSTGRES_USER')}:{env('POSTGRES_PASSWORD')}@db:5432/{env('POSTGRES_DB')}"
