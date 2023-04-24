#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By: CheerfulAnt (Github account holder) <CheerfulAnt@outlook.com>
# License: MIT License.
# ---------------------------------------------------------------------------
""" This script is part of the lotto-2023-db project. """
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from json import load
from dotenv import dotenv_values
from pydantic import BaseModel
from inflection import underscore

config = {
    **dotenv_values('.env.secret'),
    **dotenv_values('.env.shared')
}


# Casting configuration variables from strings.

class ConfigCast(BaseModel):
    # .env.shared
    LOG_SIZE: int
    LOG_COUNT: int
    EXCEPTION_SHORT_SHOW: bool
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

# read from jsons

with open(config['DRAW_CONFIG'], 'r', encoding=config['ENCODING']) as j_file:
    draw_config_json = load(j_file)

with open(config['REQUESTS_JSON'], 'r', encoding=config['ENCODING']) as j_file:
    requests_json = load(j_file)

mandatory_tables = tuple(draw_config_json['mandatory_tables'])

main_games = tuple(draw_config_json['main_games'])

print(mandatory_tables)

print(main_games)
