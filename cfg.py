# load and cast variables from .env.secret and .env.shared files

from dotenv import dotenv_values
from pydantic import BaseModel

config = {
    **dotenv_values('.env.secret'),
    **dotenv_values('.env.shared')
}

# Casting configuration variables from strings.


class ConfigCast(BaseModel):
    # .env.shared
    LOG_SIZE: int
    LOG_COUNT: int
    EXCEPTION_SHOW: bool
    EMAIL_ERROR_LOG: bool
    EMAIL_EVENT_LOG: bool
    CHUNK_SIZE: int
    # .env.secret
    EMRE_SMTP_PORT: int


config_cast = ConfigCast(**config)

config.update(config_cast)

db_config = {'dbname': config['DB_DATABASE'],
             'user': config['DB_USER'],
             'password': config['DB_PASSWORD'],
             'host': config['DB_HOST']
             }
