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
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import psycopg  # psycopg3.1.8
from inflection import underscore


class DB:
    def __init__(self):
        try:
            self.conn = psycopg.connect(**cfg.db_config)
            message = 'Ok, can establish connection.'
            event_report.event_log(event='[INFO]', subject=message, message=message)
        except psycopg.OperationalError as e:
            message = 'Can NOT establish connection. Check .env config for DB settings.'
            event_report.event_log(event='[ERROR]', subject=str(e), message=message)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def conn_status(self):
        if hasattr(self, 'conn'):
            print('\033[32mConnection OK.\033[0m')
        else:
            print('\033[91mConnection FAILED.\033[0m')

    def table_exists(self, table_name):
        cur = self.conn.cursor()

        cur.execute('SELECT EXISTS(SELECT table_name FROM information_schema.tables WHERE table_name=%s)',
                    (table_name,))
        table_exists = cur.fetchone()[0]

        cur.close()

        return table_exists

    def table_create(self, table_name):
        cur = self.conn.cursor()

        cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}(
                                id INT  primary key GENERATED ALWAYS AS IDENTITY,
                                main_draw_name TEXT NULL,
                                main_draw_id INT  NULL,
                                draw_name TEXT NULL,
                                draw_id    INT    NULL,
                                draw_date   DATE     NULL,
                                draw_time   TIME     NULL,
                                results     INTEGER ARRAY    NULL,
                                special_results INTEGER ARRAY NULL);''')
        self.conn.commit()

        print(f'\033[32mTable\033[0m \033[34m{table_name}\033[0m \033[32mcreated.\033[0m')
        cur.close()

    def table_drop(self, *args):
        cur = self.conn.cursor()

        for item in args:
            cur.execute(f'DROP TABLE IF EXISTS {item}')
            self.conn.commit()

        cur.close()

    def check_last_draw_db(self, game):
        cur = self.conn.cursor()

        cur.execute(f'SELECT MAX(draw_id) FROM {game};')
        last_draw_id = cur.fetchone()

        cur.close()

        return last_draw_id[0]

    def load_data(self, games_dict):
        cur = self.conn.cursor()

        for game in games_dict.keys():
            with cur.copy(f"COPY {underscore(game)} (main_draw_id, draw_id, draw_date, draw_time, results, special_results) FROM STDIN") as copy:
                for record in games_dict[game]:
                    copy.write_row(record)

        self.conn.commit()
        cur.close()

    def get_games(self):
        cur = self.conn.cursor()

        cur.execute('SELECT game_name, game_last_draw FROM games')
        games = cur.fetchall()

        cur.close()

        return games

    def draw_id_exists(self, draw_name, draw_id):
        cur = self.conn.cursor()

        cur.execute(f'SELECT EXISTS(SELECT id FROM {draw_name} WHERE draw_id={draw_id})')

        draw_id_exists = cur.fetchone()[0]

        cur.close()

        return draw_id_exists


# CREATE TABLE IF NOT EXISTS games(
#                             game_id        SERIAL    NOT NULL,
#                             game_name      TEXT        NULL,
#                             game_last_draw INT         NULL,
#                          PRIMARY KEY(game_id));

# CREATE TABLE IF NOT EXISTS super_szansa_rel(
#                                 id INT  primary key GENERATED ALWAYS AS IDENTITY,
#                                 main_draw_name TEXT NULL,
#                                 main_draw_id INT  NULL,
#                                 draw_name TEXT NULL,
#                                 draw_id    INT    NULL);