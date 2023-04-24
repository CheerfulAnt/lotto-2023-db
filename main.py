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

# verbose or silent mode -> log to app.log
# deamon mode, to!do cron process checking
# daemon mode -> run x time after draw
# 1 retry after null value, after 15 min
# global update at 00:00


# python cli params - verbose daemon ect.

print('Checking Lotto API Endpoint...')     # !!!!!!!!!

print('Checking database connection...')
db_obj = dbq.DB()
db_obj.conn_status()

print('Checking existing tables...')    # !!!!!!!!!
tables_db = [item[0] for item in db_obj.get_tables()]

print('\033[34m', end='')
print(*tables_db, sep='\n')
print('\033[0m', end='')

if all([item in tables_db for item in cfg.mandatory_tables]):
    print('\033[32mAll mandatory tables exists.\033[0m')
    print('Be patient, fetching data in progress...')
    print('\033[32mData fetching completed. 2345434535 new records in database\033[0m')
else:
    print('Seems as first run or problem with mandatory tables...')
    print('Deleting existing tables...')
    # db_obj.table_drop(*cfg.game_subtype_list_sc)  # !!!!!!!!!
    print('Be patient, fetching data in progress...')
    print('\033[32mData fetching completed. 2345434535 new records in database\033[0m')


