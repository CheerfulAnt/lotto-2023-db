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


def chunks_generator(last, chunk):

    chunks_list = list()

    if last <= chunk:
        chunks_list.append((1, last, last))
        return chunks_list

    def chungen(last, chunk):

        aux_list = list()
        rest = last % chunk
        base = last - rest
        index_qty = int(base / chunk)

        if len(chunks_list):
            last_hop = chunks_list[-1][-1]
        else:
            last_hop = 0

        hop = index_qty * chunk
        chunk_qty = int((hop - last_hop) / chunk)
        for _ in range(chunk_qty):
            hop = index_qty * chunk
            aux_list.insert(0, (index_qty, chunk, hop))
            index_qty -= 1
        chunks_list.extend(aux_list)
        aux_list.clear()
        return rest

    rest = chungen(last=last, chunk=chunk)

    dividers = list()

    for i in range(1, chunk + 1):
        if chunk % i == 0:
            dividers.append(i)

    dividers.reverse()
    dividers_qty = len(dividers)

    for x in range(dividers_qty):
        if x + 1 == dividers_qty:
            break

        if dividers[x + 1] <= rest < dividers[x] and rest > 0:
            chunk = dividers[x + 1]
            rest = chungen(last=last, chunk=chunk)

    return chunks_list


print(chunks_generator(6856, 1000))


# fetch draws

# db_obj = dbq.DB()
#
# for item in cfg.game_type_list:
#     print(item)
#     last_game_id = check_last_draw(game_type=item)
#     print(cfg.game_dict[item][0])
#     last_game_id_db = db_obj.check_last_draw_db(cfg.game_dict[item][0])
#     chunk_size = cfg.config['CHUNK_SIZE']
#     print('last id ', last_game_id)
#     print('last id db ', last_game_id_db)
#     time.sleep()
#     if last_game_id_db is None:
#         pass
