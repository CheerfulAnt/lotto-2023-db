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
import argparse

if sys.version_info < (3, 10):
    raise Exception('Tested only on Python 3.10 :-)')

parser = argparse.ArgumentParser()
parser.parse_args()

# -- to do - db updates --
# daily - all games update - 00:00 or on script run
# Lotto: Tuesdays, Thursdays and Saturdays at 22:00
# Eurojackpot: On Fridays between 20.00 and 21.00 and on Tuesdays between 20:15 and 21:00
# Keno: Every 4 minutes
# Szybkie 600: Every 4 minutes
# Multi Multi: Daily at 14:00 and 22:00
# Ekstra Pensja: Daily at 22:00
# Mini Lotto: Daily at 22:00
# Kaskada: Daily at 14:00 and 22:00

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

aaa = list()


if all([item in tables_db for item in cfg.mandatory_tables]):
    print('\033[32mAll mandatory tables exists.\033[0m ', end='')
    print('\033[34m[', end='')
    print(*cfg.mandatory_tables, sep=';', end='')
    print(']\033[0m', end='\n')
    print('Proceeding to data fetching, be patient...')
    print('\033[32mData fetching completed. 2345434535 new records in database\033[0m')

elif not all([item in tables_db for item in cfg.mandatory_tables]) and len(tables_db) > 0:
    print('\033[91mMandatory tables not found, but there are tables with the results, script aborted.\033[0m')
    sys.exit()
else:
    print('Seems as first run, creating mandatory tables...')
    print('Be patient, fetching data in progress...')
    print('Proceeding to data fetching, be patient...')
    print('\033[32mData fetching completed. 2345434535 new records in database\033[0m')


# db_obj.table_drop(*cfg.game_subtype_list_sc)  # !!!!!!!!!

