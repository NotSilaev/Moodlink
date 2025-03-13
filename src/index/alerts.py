import sys
sys.path.append('..')

from config import settings
from api.telegram import telegramAPIRequest
from logs import addLog

from index.utils import getIndexMeta

from database.clickhouse import client as clickhouse_client

from textwrap import dedent


async def sendAlert(index_value: int, index_change: int) -> None:
    '''Sends Telegram alerts to all recipients whose level has been breached by the index.
    
    :param index_value: new index value.
    :param index_change: the positive number of index points has been changed.
    '''

    await addLog(
        level='INFO',
        text='Sending of index change alerts has started.'
    )

    index_title, index_emoji = getIndexMeta(index_value)

    query = f'''
        SELECT user_id
        FROM alerts
        WHERE alert_level <= {index_change}
    '''
    recepients = clickhouse_client.query(query).result_rows

    for recepient_row in recepients:
        recepient = recepient_row[0]

        try:
            await telegramAPIRequest(
                bot_token=settings.telegram_bot_token,
                request_method='POST',
                api_method='sendMessage',
                parameters={
                    'chat_id': recepient,
                    'text': dedent(
                        f'''
                        <b>🔔 Индекс изменился на {index_change} (пп.)!</b>

                        {index_emoji} Показатель индекса: <b>{index_value} <i>({index_title})</i></b>
                        '''),
                    'parse_mode': 'HTML',
                }
            )
        except Exception as e:
            await addLog(
                level='ERROR',
                text=f'Sending index change alert failed with an error: {str(e)} (recepient: {recepient})'
            )

    await addLog(
        level='INFO',
        text=f'Sending index change alerts was finished.'
    )
