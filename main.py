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
import fetch_draw as fedr
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import sys


if sys.version_info < (3, 10):
    raise Exception('Tested only on Python 3.10 :-)')

print()

print('Checking Lotto API Endpoint...')

resp_stat_code = fedr.get_draws(response_status_code=True)

if resp_stat_code == 200:
    print(f'\033[32mResponse status code: {resp_stat_code}, looks good...\033[0m') # !!! Event Log
else:
    print(f'\033[91mSomething goes wrong. Response status code: {resp_stat_code}.\033[0m')  # !!! Event Log


print('Checking database connection...')
db_obj = dbq.DB()
db_con_stat = db_obj.conn_status()

if db_con_stat == 0:
    print('\033[32mConnection OK.\033[0m')
else:
    print('\033[91mConnection FAILED.\033[0m')

print('Checking existing tables...')    # !!!!!!!!!
tables_db = [item[0] for item in db_obj.get_tables()]

# print('\033[34m', end='')
# print(*tables_db, sep='|')
# print('\033[0m', end='')

if all([item in tables_db for item in cfg.mandatory_tables]):
    print('\033[32mAll mandatory tables exists.\033[0m ', end='')
    print('\033[34m[', end='')
    print(*cfg.mandatory_tables, sep=';', end='')
    print(']\033[0m', end='\n')
    print('Proceeding to data fetching, be patient...')
    print('\033[32mData fetching completed. 2345434535 new records in database\033[0m')
else: # !!! if mandatory tables not exist but tables with data exist, stop and send info  email to the further investigation
      # if mandatory tables not exist create, and start fetching data
    print('Seems as first run or problem with mandatory tables...')  # !!! check if first run, don't fetch 500k records xD
    print('Deleting existing tables...')
    # db_obj.table_drop(*cfg.game_subtype_list_sc)  # !!!!!!!!!
    print('Be patient, fetching data in progress...')
    print('\033[32mData fetching completed. 2345434535 new records in database\033[0m')


