# to!do: make class with show all variables method
# load and cast variables from .env.secret and .env.shared files

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

# prepare lists with game names, *_sc - lower case & snake case names for DB

games = tuple(draw_config_json['game_type'])

# game_dict = dict()
# game_sub_tuple = tuple()
# game_type_list = list()
# game_subtype_list = list()
# game_type_list_sc = list()
# game_subtype_list_sc = list()

# for key in draw_config_json['game_type'].keys():
#
#     game_type_list.append(key)
#     game_type_list_sc.append(underscore(key))
#
#     for sub_key in draw_config_json['game_type'][key]['game_subtype'].keys():
#         game_subtype_list.append(sub_key)
#         game_subtype_list_sc.append(underscore(sub_key))
#         game_sub_tuple = game_sub_tuple + (underscore(sub_key), )
#
#     game_dict[key] = game_sub_tuple
#     game_sub_tuple = tuple()

print(games)