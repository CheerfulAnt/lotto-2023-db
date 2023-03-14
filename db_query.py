# !!! in progress !!! (PostgreSQL)
import sys

import cfg
import event_report
# -----------------------------
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

    def table_exists(self, *args):
        cur = self.conn.cursor()
        table_exists_dict = dict()

        for item in args:
            cur.execute('SELECT EXISTS(SELECT table_name FROM information_schema.tables WHERE table_name=%s)',
                        (item,))
            table_exists_dict[item] = cur.fetchone()[0]

        cur.close()

        return table_exists_dict

    def table_create(self, *args):
        cur = self.conn.cursor()

        tables_dict = self.table_exists(*args)

        for key, value in tables_dict.items():
            if not value:

                cur.execute(f'''CREATE TABLE IF NOT EXISTS {key}(
                            draw_id    INT    NULL,
                            draw_date   DATE        NULL,
                            draw_time   BOOLEAN     NULL,
                            results   integer ARRAY    NULL,
                            special_results integer ARRAY NULL,
                            draw_sum    INT         NULL,
                            draw_avg    INT         NULL,
                            draw_median INT         NULL,
                            draw_odd    INT         NULL,
                            draw_even   INT         NULL,
                            draw_one_digit    INT   NULL,
                            draw_two_digit    INT   NULL,
                            prime_numbers_qty INT   NULL,
                            leap_year   BOOLEAN     NULL,
                            draw_date_sum INT       NULL,
                            birth_number INT        NULL,
                            master_number INT       NULL,
                         PRIMARY KEY(draw_id));''')
                self.conn.commit()

                print(f'\033[32mTable\033[0m \033[34m{key}\033[0m \033[32mcreated.\033[0m')
        cur.close()

    def table_drop(self, *args):
        cur = self.conn.cursor()

        for item in args:
            cur.execute(f'DROP TABLE IF EXISTS {item}')
            self.conn.commit()

        cur.close()

    def check_last_draw_db(self, game_subtype):
        cur = self.conn.cursor()

        cur.execute(f'SELECT MAX(draw_id) FROM {game_subtype};')
        last_draw_id = cur.fetchone()

        cur.close()

        return last_draw_id[0]

    def load_data_db(self):
        cur = self.conn.cursor()
        cur.close()
