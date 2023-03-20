#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By: CheerfulAnt (Github account holder) <CheerfulAnt@outlook.com>
# Project: lotto-2023-db
# Version 0.2.0
# License: MIT License.
# ---------------------------------------------------------------------------
""" *Work in progress.*
    The script retrieves results from the lotto website.
    In the final version, the script will retrieve the draws results
    from the lotto website and load it into the database.
    """
# ---------------------------------------------------------------------------
# Imports from lotto-2023-db
# ---------------------------------------------------------------------------
import cfg
import db_query as dbq
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
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

