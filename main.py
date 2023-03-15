#!/usr/bin/python3
# Project Name: lotto-2023-db
# Description: I don't know what is this, work in progress :-)
#              Tested on Linux, Ubuntu 22.04.2
# Usage: main.py :-)
# Author: CheerfulAnt@outlook.com
# Version: 0.1.0
# Date: 1 March 2023 - 21:00 (GMT+01:00)

import cfg
#import event_report
#import fetch_draw
import db_query as dbq
# -------------------
import sys


if sys.version_info < (3, 10):
    raise Exception('Tested only on Python 3.10 :-)')

print()
print('Checking database connection...')
db_obj = dbq.DB()
db_obj.conn_status()
#db_obj.table_drop(*cfg.game_subtype_list_sc)
print('Checking existing tables...')
tables = db_obj.table_exists(*cfg.game_subtype_list_sc)
create_table = False
for key, value in tables.items():
    print(f'\033[34m{key}\033[0m: \033[33m{value}\033[0m')
    if not value:
        create_table = True
if create_table:
    draw_config = cfg.config['DRAW_CONFIG']
    print(f'Creating not existing tables according to {draw_config}')
    db_obj.table_create(*cfg.game_subtype_list_sc)

print('Initialization of loading data into the database')

