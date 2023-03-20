#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By: CheerfulAnt (Github account holder) <CheerfulAnt@outlook.com>
# License: MIT License.
# ---------------------------------------------------------------------------
""" This script is part of the lotto-2023-db project. """
# ---------------------------------------------------------------------------
# Imports from lotto-2023-db
# ---------------------------------------------------------------------------
import cfg
import event_report
import db_query as dbq
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import requests

# function check_last_draw() checks last draw id for games from lotto website. (or get range)


def get_draws(game=cfg.config['DEFAULT_GAME'], index=1, size=1, order='DESC', get_id=True):
    # get data to build request

    base_url = cfg.draw_config_json['base_url']
    headers = cfg.requests_json['headers']
    params = cfg.draw_config_json['query_strings']

    params['game'] = game
    params['index'] = index
    params['size'] = size
    params['order'] = order

    # get last draw

    response = requests.get(base_url, headers=headers, params=params)

    # check response.status_code, if not 200, raise Exception - CustomError

    if response.status_code != 200:
        message = 'Game "' + game + '" - Cannot fetch json data, status code: ' + str(response.status_code)
        raise event_report.CustomError(message)

    # get last drawSystemId

    game_data = response.json()

    # check if drawSystemId is None, if yes, probably update after draw in lotto system
    # if not None get draw  ID and draw date

    if game_data['items'][0]['drawSystemId'] is None:
        message = 'Game "' + game + '" - Cannot fetch json data, drawSystemId is None.'
        raise event_report.CustomError(message)

    if get_id:
        return game_data['items'][0]['drawSystemId']

    return game_data


# to!do:  !!! sort=drawSystemId, super szansa LOTTO check if was another subgames (when het and parse) !!
# desc if load new draws and ASC when initial load

def chunks_generator(number, chunk=cfg.config['CHUNK_SIZE'], order='ASC'):
    chunks_list = list()

    if number <= chunk:
        chunks_list.append((1, number, number))
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

    rest = chungen(last=number, chunk=chunk)

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
            rest = chungen(last=number, chunk=chunk)

    if order == 'DESC':
        chunks_list.reverse()
        return chunks_list

    return chunks_list


db_obj = dbq.DB()

games = db_obj.get_games()

games_dict = dict()

for game in games:

    last_draw_id = (get_draws(game=game[0]))

    if game[1] is None: pass  # get and load all
        #print(chunks_generator(last_draw_id))
    else:
        id_to_get = last_draw_id - game[1]
        #print(id_to_get)
        #print(get_draws())
        chunks = chunks_generator(id_to_get, order='ASC')
        #print(chunks)
        for chunk in chunks:
            #print(chunk)
            draws_data = get_draws(game[0], index=chunk[0], size=chunk[1], order='DESC', get_id=False)
            # #draws_data = json.dumps(draws_data, indent=4)
            #print(draws_data)
            # set True if checked and if (don't check every iteration)
            for item in draws_data['items']:

                for results in item['results']:
                    if results['gameType'] not in games_dict:
                        games_dict[results['gameType']] = []
                    games_dict[results['gameType']].append((results['drawSystemId'], results['drawDate'], results['resultsJson']))


print('list_test:', games_dict)

for x in games_dict.keys():
    print(x)

# fetch draws

# !!! Not ready as all scripts and fn :) if all load all draws from draw_config.json to db or check and load missing,
# else load only one draw e.g. Lotto,
# first check if exists in draw_config.json

def load_to_db(draws='all'):
    if draws == 'all':

        db_obj = dbq.DB()

        for game in cfg.game_type_list:
            print(game)
            last_game_id = get_draws(game_type=game)
            print(cfg.game_dict[game][0])
            last_game_id_db = db_obj.check_last_draw_db(cfg.game_dict[game][0])

            print('last id ', last_game_id)
            print('last id db ', last_game_id_db)

            if last_game_id_db is not None and last_game_id > last_game_id_db:
                chunks_list = chunks_generator(6856)

                # sprawdz czy juz jest coś w bazie danych

            print(chunks_list)
            chunks_list.clear()

            if last_game_id_db is None:
                pass

            for chunk in chunks_list:
                #   fetch
                pass

            # chunks_list = chunks_generator()
            # print(chunks_list)
            chunks_qty = len(chunks_list)
            chunks_counter = 0
    else:
        # check if is in json
        pass

# load_to_db()
