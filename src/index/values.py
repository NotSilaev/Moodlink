import sys
sys.path.append('..')

from logs import addLog

from database.clickhouse import client as clickhouse_client

import datetime


async def setIndexValue(
    value: int, 
    greed_msg_count: int, 
    fear_msg_count: int, 
    neutral_msg_count: int, 
    updated_at: datetime.datetime 
) -> None:
    try:
        query = f'''
            INSERT INTO index_values (value, greed_msg_count, fear_msg_count, neutral_msg_count, updated_at)
            VALUES ({value}, {greed_msg_count}, {fear_msg_count}, {neutral_msg_count}, '{updated_at}')
        '''
        clickhouse_client.command(query)

        await addLog(
            level='INFO',
            text=f"New index value successfully saved."
        )

    except Exception as e:
        await addLog(
            level='CRITICAL',
            text=f"New index value isn't saved: {str(e)}"
        )


def getLastIndexUpdates(limit: int = 1) -> list[dict]:
    index_updates = []

    query = f'''
        SELECT value, updated_at
        FROM index_values
        ORDER BY id DESC
        LIMIT {limit}
    '''
    rows = clickhouse_client.query(query).result_rows
    if rows:
        for index_data in rows:
            value = index_data[0]
            updated_at = index_data[1]
            index_updates.append({
                'value': value,
                'updated_at': updated_at
            })
    else:
        index_updates.append({
            'value': 50, # Neutral
            'updated_at': None
        })

    return index_updates


def getIndexValuesByPeriod(period: tuple[datetime.datetime, datetime.datetime], hour_gap=1) -> dict[str: int]:
    '''Generates a dictionary mapping time points to their corresponding index values.

    This function retrieves index values from the database at specified time intervals 
    within a given period.

    :param period: A tuple containing the start and end timestamps of the period.
    :param hour_gap: The time interval (in hours) between consecutive index queries.
    :return: A dictionary where keys are time strings ('%H:%M'), and values are index values.
    '''

    try:
        start_timestamp = period[0]
        end_timestamp = period[1]
    except IndexError:
        raise ValueError('Period tuple must contain two elements: start_timestamp and end_timestamp.')

    if start_timestamp > end_timestamp:
        raise ValueError('start_timestamp cannot be higher then end_timestamp.')

    index_hourly_values = dict()

    all_day_index_updates: list[dict] = getLastIndexUpdates(limit=24)[::-1]
    for update in all_day_index_updates:
        index_hourly_values[update['updated_at']] = update['value']

    return index_hourly_values