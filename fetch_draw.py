import time

import cfg
import event_report
import db_query as dbq
# --------------------
import os
import requests
import json
import ijson
import pandas as pd
from datetime import datetime


# function check_last_draw() checks last draw id for games subtypes from lotto website.

def check_last_draw(game_type=cfg.config['DEFAULT_GAME']):
    # # get data to build request
    #
    # base_url = cfg.draw_config_json['base_url']
    # headers = cfg.requests_json['headers']
    # params = cfg.draw_config_json['query_strings']
    #
    # params['game'] = game_type
    #
    # # get last draw
    #
    # response = requests.get(base_url, headers=headers, params=params)
    #
    # # check response.status_code, if not 200, raise Exception - CustomError
    #
    # if response.status_code != 200:
    #     message = 'Game "' + game_type + '" - Cannot fetch json data, status code: ' + str(response.status_code)
    #     raise event_report.CustomError(message)
    #
    # # get last drawSystemId
    #
    # last_game = response.json()
    #
    # # check if drawSystemId is None, if yes, probably update after draw in lotto system
    # # if not None get draw  ID and draw date
    #
    # if last_game['items'][0]['drawSystemId'] is None:
    #     message = 'Game "' + game_type + '" - Cannot fetch json data, drawSystemId is None.'
    #     raise event_report.CustomError(message)
    #
    # last_game_id = last_game['items'][0]['drawSystemId']

    last_game_id = 6856

    return last_game_id


# fetch draws

db_obj = dbq.DB()

for item in cfg.game_type_list:
    print(item)
    last_game_id = check_last_draw(game_type=item)
    print(cfg.game_dict[item][0])
    last_game_id_db = db_obj.check_last_draw_db(cfg.game_dict[item][0])
    chunk_size = cfg.config['CHUNK_SIZE']
    print('last id ', last_game_id)
    print('last id db ', last_game_id_db)

    if last_game_id_db is None:
        if last_game_id / chunk_size <= 1:
            print('None by once: ', last_game_id)
            # fetch all by once
            # index = last_game_id
            # size = last_game_id
        else:
            iter_cnt = last_game_id // chunk_size
            index = last_game_id
            # size = chunk_size
            for i in range(iter_cnt + 1):
                #time.sleep(2)
                print(f'index={index}&size={chunk_size}')
                if index < chunk_size:
                    chunk_size = index
                else:
                    index -= chunk_size




    # if last_game_id > last_game_id_db:
    #     pass

