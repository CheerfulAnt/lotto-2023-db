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
import json
import requests
from datetime import datetime
from inflection import underscore


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
        if order == 'DESC':
            message = 'Game "' + game + '" - Cannot fetch json data, drawSystemId is None.'
            raise event_report.CustomError(message)
        if order == 'ASC':  # null id value after draws (up to approx. 30min), appear as first in asc
            # should return last index + 1 to!do
            response = requests.get(base_url, headers=headers, params=params)

            # check response.status_code, if not 200, raise Exception - CustomError

            if response.status_code != 200:
                message = 'Game "' + game + '" - Cannot fetch json data, status code: ' + str(response.status_code)
                raise event_report.CustomError(message)

            game_data = response.json()

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

# to!do instead of a separate table check from the game table

# after initial update clean tables, none values, remove duplicates, 'subgames' draws can appear in another 'main draws'
# messy query results
# after add new master game

# fetch and load results into database, tested on Lotto and EkstraPensja

games = db_obj.get_games()

games_dict = dict()
super_szansa_rel_dict = dict()

for game in games:  # lotto order little messy, doesn't start from first draw

    last_draw_id = (get_draws(game=game[0], order='DESC'))
    first_draw_id = (get_draws(game=game[0], order='ASC'))

    draw_qty = last_draw_id - first_draw_id

    # last_draw_id = 6859

    if game[1] is None:
        pass  # get and load all

    # print(chunks_generator(last_draw_id))
    else:
        if last_draw_id < game[1]:
            print('Something goes wrong !!! EventReport')  # !!!!!!!!!!!!!!!!!!!!
            id_to_get = None
        elif last_draw_id > game[1]:
            id_to_get = last_draw_id - game[1]
        elif last_draw_id == game[1]:
            print('Nothing to do...')
            id_to_get = None
            break
        else:
            print('EventReport')  # !!!!!!!!!!!!!!!!!!!!
            id_to_get = None

        chunks = chunks_generator(draw_qty, order='ASC')

        for chunk in chunks:
            games_dict.clear()
            super_szansa_rel_dict.clear()

            draws_data = get_draws(game[0], index=chunk[0], size=chunk[1], order='DESC', get_id=False)

            for item in draws_data['items']:

                for results in item['results']:      # underscore one time variable

                    if results['gameType'] not in games_dict:
                        games_dict[results['gameType']] = []
                        super_szansa_rel_dict['SuperSzansa'] = []
                        game_subtype_name_sc = underscore(results['gameType'])
                        if not db_obj.table_exists(game_subtype_name_sc):  # to!do insert new game name to game table
                            db_obj.table_create(game_subtype_name_sc)

                    date_time_obj = datetime.strptime(results['drawDate'], '%Y-%m-%dT%H:%M:%SZ')
                    draw_date = date_time_obj.strftime('%Y-%m-%d')
                    draw_time = date_time_obj.strftime('%H:%M:%S')

                    if results['gameType'] != 'SuperSzansa' and results['drawSystemId'] is not None:
                        games_dict[results['gameType']].append(
                            (item['gameType'], item['drawSystemId'], results['gameType'],
                             results['drawSystemId'], draw_date, draw_time, results['resultsJson'],
                             results['specialResults']))

                    if results['gameType'] == 'SuperSzansa' and results['drawSystemId'] is not None:     # SuperSzansa exists only with another games
                        if not db_obj.draw_id_exists(underscore(results['gameType']), results['drawSystemId']):
                            games_dict[results['gameType']].append(
                                (item['gameType'], item['drawSystemId'], results['gameType'],
                                 results['drawSystemId'], draw_date, draw_time, results['resultsJson'],
                                 results['specialResults']))
                        #print(item['gameType'], item['drawSystemId'],
                        #                                            results['gameType'], results['drawSystemId'])
                        super_szansa_rel_dict['SuperSzansa'].append((item['gameType'], item['drawSystemId'],
                                                                    results['gameType'], results['drawSystemId']))

            print(super_szansa_rel_dict)
            #db_obj.load_data(games_dict)

            # to!do update games table and last draws subgames IDs


# draw_qty = last_draw_id - first_draw_id on system update
# Traceback(most recent call last):
# File     "/home/kate/PycharmProjects/lotto-2023-db/fetch_draw.py", line
# 154, in < module >  draw_qty = last_draw_id - first_draw_id TypeError: unsupported operand
# type(s)for -: 'int' and 'NoneType'
