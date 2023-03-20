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
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import os
import sys
import traceback
import smtplib
import ssl
from email.message import EmailMessage
import logging
from logging.handlers import RotatingFileHandler

# check if directory for log files exists if not - create
file_dir_exist = os.path.exists(cfg.config['LOG_DIR'])

if not file_dir_exist:
    os.makedirs(cfg.config['LOG_DIR'])

# log rotation
logger = logging.getLogger(cfg.config['PROJECT_NAME'])
logger.setLevel(logging.DEBUG)
fh = RotatingFileHandler(filename=cfg.config['LOG_FILE'], maxBytes=cfg.config['LOG_SIZE'],
                         backupCount=cfg.config['LOG_COUNT'], encoding=cfg.config['ENCODING'])
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[{asctime}] - [{name}] - [{levelname}] - {message}', style="{")
fh.setFormatter(formatter)
logger.addHandler(fh)


def event_log(exception_short_show=cfg.config['EXCEPTION_SHORT_SHOW'],
              exception_show=cfg.config['EXCEPTION_SHOW'],
              email_error_log=cfg.config['EMAIL_ERROR_LOG'],
              email_event_log=cfg.config['EMAIL_EVENT_LOG'],
              event='[UNKNOWN]',
              subject='',
              message='No message.'):

    if event == '[ERROR]':
        logger.exception('Surprise, [ERROR] occurred.')
        if exception_show:
            print('\033[91m' + traceback.format_exc() + '\033[0m')
        if email_error_log:
            subject = event + ' - ' + subject
            send_email(subject=subject, message=traceback.format_exc())
        if exception_short_show:
            print('\033[91m' + message + '\033[0m')
            print('\033[91mExiting... \033[0m')
            sys.exit(1)
    else:
        logger.info(event + ' ' + message)
        if email_event_log:
            subject = event + ' - ' + subject
            send_email(subject=subject, message=message)


def send_email(emre_user=cfg.config['EMRE_USER'],
               emre_pass=cfg.config['EMRE_PASS'],
               emre_smtp_srv=cfg.config['EMRE_SMTP_SRV'],
               emre_smtp_port=cfg.config['EMRE_SMTP_PORT'],
               project_name=cfg.config['PROJECT_NAME'],
               subject="No subject.",
               message='No message.'):

    msg = EmailMessage()
    msg['Subject'] = '[' + project_name + '] ' + subject
    msg['From'] = emre_user
    msg['To'] = emre_user
    msg.set_content(message)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(emre_smtp_srv, emre_smtp_port, timeout=2) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(emre_user, emre_pass)
            server.send_message(msg)
            server.quit()
    except Exception:
        logger.exception('Surprise, [ERROR] occurred. Can\'t sent e-mail.')


class CustomError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
