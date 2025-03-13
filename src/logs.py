from config import settings

from api.telegram import telegramAPIRequest

import os
import datetime
import logging
from textwrap import dedent


# Create a custom formatter with your desired time format
time_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] - %(message)s', datefmt=time_format)

# Create a logger and set the custom formatter
logger = logging.getLogger('custom_logger')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


async def addLog(level: str, text: str, send_telegram_alert: bool = False) -> None:
    '''Adds new log to file, console and telegram chat.

    :param level: log level (`info`, 'debug', 'warning', 'error', 'critical').
    :param text: log text.
    :param send_telegram_alert: determines whether a log will be sent to telegram chat.
    '''
    
    now = datetime.datetime.now()
    path = f"logs/{now.year}/{now.month}/{now.day}/"
    filename = path + f"log-{now.hour}.log"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(filename, 'a') as file:
        separator_string = f"\n\n{'='*50}\n\n"
        try:
            file.write(f"{now} [{level.upper()}] - {text}" + separator_string)
        except:
            file.write(f"{now} [{level.upper()}] - {text.encode('utf-8')}" + separator_string)

    if send_telegram_alert:
        disable_notification = True
        if level.upper() in ['ERROR', 'CRITICAL']:
            disable_notification = False

        for recepient in settings.logs_recepients:
            await telegramAPIRequest(
                bot_token=settings.telegram_logs_bot_token,
                request_method='POST',
                api_method='sendMessage',
                parameters={
                    'chat_id': recepient,
                    'text': dedent(
                        f'''
                        *[{level.upper()}]* _({now})_

                        `{text}`
                        '''),
                    'parse_mode': 'Markdown',
                    'disable_notification': disable_notification,
                }
            )