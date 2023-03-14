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

    # get data to build request

    base_url = cfg.draw_config_json['base_url']
    headers = cfg.requests_json['headers']
    params = cfg.draw_config_json['query_strings']

    params['game'] = game_type

    # get last draw

    response = requests.get(base_url, headers=headers, params=params)

    # check response.status_code, if not 200, raise Exception - CustomError

    if response.status_code != 200:
        message = 'Game "' + game_type + '" - Cannot fetch json data, status code: ' + str(response.status_code)
        raise event_report.CustomError(message)

    # get last drawSystemId

    last_game = response.json()

    # check if drawSystemId is None, if yes, probably update after draw in lotto system
    # if not None get draw  ID and draw date

    if last_game['items'][0]['drawSystemId'] is None:
        message = 'Game "' + game_type + '" - Cannot fetch json data, drawSystemId is None.'
        raise event_report.CustomError(message)

    last_game_id = last_game['items'][0]['drawSystemId']

    #last_game_id = 4453

    return last_game_id


# check last draws for games subtypes in database

db_obj = dbq.DB()

for item in cfg.game_type_list:
    print(item)
    print(check_last_draw(game_type=item))
    print(cfg.game_dict[item][0])
    print(db_obj.check_last_draw_db(cfg.game_dict[item][0]))
    # print(dbq.check_last_draw_db(cfg.game_dict[item][0]))



# do not call get_to_json(), this will kill draw_config.json :-)
# file names for game data: gameName_base.json, gameName.json, gameName.csv
# function save_json_csv() only for Lotto (Lotto_base.json include Lotto and LottoPlus, exclude some fields,
# e.g. specialResults

# Function get() - fetch draws, if file does not exist, dump results to json file (gameName_base.json).
# If file exist, check last drawSystemId in file and from request, update gameName_base.json if
# drawSystemId's not equal.
# Unfortunately get() for fetching all data, in this version works only with a small number of draws, e.g.
# Lotto (approx. 7k results), EkstraPremia (approx. 2.5k results)
# For e.g. Szybkie600 returns error: {"code":500,"message":"Internal server error"} (approx. 300k results).
# It will be fixed in the version of the function for the database, by sequential fetching.

def get_to_json(game=cfg.config['DEFAULT_GAME'], file_dir=cfg.config['DATA_DIR'], base_file=cfg.config['BASE_FILE']):
    try:

        base_file_name_path = file_dir + game + '_' + base_file

        file_dir_exist = os.path.exists(file_dir)  # check if directory for draws files exists if not - create

        if not file_dir_exist:
            os.makedirs(file_dir)

        main_json_exist = os.path.isfile(base_file_name_path)  # check if file exist

        message = ''  # for event_log - completion during code execution

        # get data to build request

        with open(cfg.config['DRAW_CONFIG'], 'r', encoding=cfg.config['ENCODING']) as j_file:
            request_data = json.load(j_file)

            request_data['query_strings']['game'] = game

        with open(cfg.config['REQUESTS_JSON'], 'r', encoding=cfg.config['ENCODING']) as j_file:
            j_requests = json.load(j_file)

        # get last draw

        response = requests.get(request_data['base_url'], headers=j_requests['headers'],
                                params=request_data['query_strings'])

        # check response.status_code, if not 200, raise Exception - CustomError

        if response.status_code != 200:
            message = 'Game "' + game + '" - Cannot fetch json data, status code: ' + str(response.status_code)
            raise event_report.CustomError(message)

        # get last drawSystemId

        last_game = response.json()

        # check if drawSystemId is None, if yes, probably update after draw in lotto system
        # if not None get draw  ID and draw date

        if last_game['items'][0]['drawSystemId'] is None:
            message = 'Game "' + game + '" - Cannot fetch json data, drawSystemId is None.'
            raise event_report.CustomError(message)

        last_game_id = last_game['items'][0]['drawSystemId']
        last_draw_date = last_game['items'][0]['drawDate']

        # create gameName_base.json file if not exist, based on last draw, 'size' param = drawSystemId - get all draws

        if not main_json_exist:

            request_data['query_strings']['size'] = last_game_id

            response = requests.get(request_data['base_url'], headers=j_requests['headers'],
                                    params=request_data['query_strings'])

            # Check response.status_code, if not 200, raise Exception - CustomError

            if response.status_code != 200:
                message = 'Game "' + game + '" - Cannot fetch json data, status code: ' \
                          + str(response.status_code) + '.'
                raise event_report.CustomError(message)

            # dump response results to gameName_base.json

            with open(base_file_name_path, 'w', encoding="utf-8") as j_file:
                json.dump(response.json(), j_file, indent=4)
                message = 'Fetched all ' + game + ' draws.'

        # if file exist, fetch only draws not present in gameName_base.json,
        # merge with existing data, save updated, new gameName_base.json

        if main_json_exist:

            # json file unordered, get all draws system ID, and check max value (last draw in file)
            # ijson - iterative json parser, instead of loading the entire file as a json object

            with open(base_file_name_path, 'r', encoding=cfg.config['ENCODING']) as j_file:
                last_game_id_file = ijson.items(j_file, 'items.item.drawSystemId')
                last_game_id_file = max(last_game_id_file)

            # check drawSystemId's from response and file, and get missing draws

            if last_game_id > last_game_id_file:

                get_size = last_game_id - last_game_id_file

                request_data['query_strings']['size'] = get_size

                response = requests.get(request_data['base_url'], headers=j_requests['headers'],
                                        params=request_data['query_strings'])

                # check response.status_code, if not 200, raise Exception - CustomError

                if response.status_code != 200:
                    message = 'Game "' + game + '" - Cannot fetch json data, status code: ' \
                              + str(response.status_code) + '.'
                    raise event_report.CustomError(message)

                # update json data

                j_data = response.json()

                with open(base_file_name_path, 'r', encoding=cfg.config['ENCODING']) as j_file:
                    j_file_data = json.load(j_file)

                for i in range(len(j_data['items'])):
                    j_file_data['items'].insert(i, j_data['items'][i])

                # save fetched data to gameName_base.json

                with open(base_file_name_path, 'w', encoding=cfg.config['ENCODING']) as j_file:
                    json.dump(j_file_data, j_file, indent=4)
                    message = 'Updated ' + game + ' draws.'

        # update data in draw_config.json

        with open(cfg.config['DRAW_CONFIG'], 'r+', encoding=cfg.config['ENCODING']) as j_file:
            j_data_update = json.load(j_file)

            j_data_update['last_run_get'] = datetime.now().replace(microsecond=0).isoformat()
            j_data_update['game_type'][game]['last_system_id'] = last_game_id
            j_data_update['game_type'][game]['last_draw_date'] = last_draw_date

            j_file.seek(0)
            json.dump(j_data_update, j_file, indent=4)
            j_file.truncate()

        if message == '':
            message = 'Nothing to do, ' + game + ' draws are up to date.'

        event_report.event_log(event='[UPDATE]', subject=message, message=message)
    except event_report.CustomError as ce:
        event_report.event_log(event='[ERROR]', subject=str(ce)[1:-1])
    except Exception as e:
        event_report.event_log(event='[ERROR]', subject=str(e))


# do not call get_to_json(), this will kill draw_config.json :-)

# with open(cfg.config['DRAW_CONFIG'], 'r', encoding=cfg.config['ENCODING']) as j_file:
#     j_data = json.load(j_file)
#
# for key in j_data['game_type'].keys():
#     get_to_json(game=key)


# Function save_json_csv() for fun, not ready, but works :-) It probably won't be developed :-)
# Do not use this function in the real world! :-) Can parse only Lotto json file with items Lotto and LottoPlus.

def save_json_csv(game=cfg.config['DEFAULT_GAME'], file_dir=cfg.config['DATA_DIR'], base_file=cfg.config['BASE_FILE']):
    try:

        base_file_name_path = file_dir + game + '_' + base_file
        json_lotto_file = file_dir + 'Lotto.json'
        json_lotto_plus_file = file_dir + 'LottoPlus.json'
        csv_lotto_file = file_dir + 'Lotto.csv'
        csv_lotto_plus_file = file_dir + 'LottoPlus.csv'

        main_json_exist = os.path.isfile(base_file_name_path)  # check if file exist

        message = ''  # for event_log - completion during code execution

        if not main_json_exist:
            message = 'File ' + base_file_name_path + ' does not exist.'
            raise event_report.CustomError(message)

        with open(base_file_name_path, 'r', encoding=cfg.config['ENCODING']) as j_file:
            j_draws = json.load(j_file)

        draw_lotto_list = list()
        draw_lotto_dict = dict()

        draw_lotto_plus_list = list()
        draw_lotto_plus_dict = dict()

        draw_lotto_csv = list()
        draw_lotto_plus_csv = list()

        # !!! to do - check if item is Lotto or LottoPlus

        for i in range(len(j_draws['items'])):

            date_time_object = datetime.strptime(j_draws['items'][i]['results'][0]['drawDate'],
                                                 cfg.config['DATE_TIME_FORMAT'])
            draw_date = date_time_object.strftime(cfg.config['DATE_STORE_FORMAT'])
            draw_time = date_time_object.strftime(cfg.config['time_store_format'])

            draw_lotto_list.append({'drawSystemId': j_draws['items'][i]['results'][0]['drawSystemId'],
                                    'drawDate': j_draws['items'][i]['results'][0]['drawDate'],
                                    'resultsJson': j_draws['items'][i]['results'][0]['resultsJson']
                                    })

            draw_lotto_csv.append([j_draws['items'][i]['results'][0]['drawSystemId'],
                                   draw_date, draw_time, *j_draws['items'][i]['results'][0]['resultsJson']])

            if len(j_draws['items'][i]['results']) != 1:
                date_time_object = datetime.strptime(j_draws['items'][i]['results'][1]['drawDate'],
                                                     cfg.config['DATE_TIME_FORMAT'])
                draw_date = date_time_object.strftime(cfg.config['DATE_STORE_FORMAT'])
                draw_time = date_time_object.strftime(cfg.config['time_store_format'])

                draw_lotto_plus_list.append({'drawSystemId': j_draws['items'][i]['results'][1]['drawSystemId'],
                                             'drawDate': j_draws['items'][i]['results'][1]['drawDate'],
                                             'resultsJson': j_draws['items'][i]['results'][1]['resultsJson']
                                             })

                draw_lotto_plus_csv.append([j_draws['items'][i]['results'][1]['drawSystemId'],
                                            draw_date, draw_time, *j_draws['items'][i]['results'][1]['resultsJson']])

        draw_lotto_dict['Lotto'] = draw_lotto_list

        draw_lotto_plus_dict['LottoPlus'] = draw_lotto_plus_list

        j_lotto = json.dumps(draw_lotto_dict, indent=4)

        with open(json_lotto_file, "w") as j_file:
            j_file.write(j_lotto)

        j_lotto = json.dumps(draw_lotto_plus_dict, indent=4)

        with open(json_lotto_plus_file, "w") as j_file:
            j_file.write(j_lotto)

        columns = ['Draw Id', 'Date', 'Time', '1', '2', '3', '4', '5', '6']

        df = pd.DataFrame(data=draw_lotto_csv, columns=columns)

        with open(csv_lotto_file, 'w') as csv_file:
            df.to_csv(csv_file, header=columns)

        df = pd.DataFrame(data=draw_lotto_plus_csv, columns=columns)

        with open(csv_lotto_plus_file, 'w') as csv_file:
            df.to_csv(csv_file, header=columns)

        if message == '':
            message = 'save_json_csv() do not use this function in the real world! :-)'

        event_report.event_log(event='[UPDATE]', subject=message, message=message)
    except event_report.CustomError as ce:
        event_report.event_log(event='[ERROR]', subject=str(ce)[1:-1])
    except Exception as e:
        event_report.event_log(event='[ERROR]', subject=str(e))

# save_json_csv()
