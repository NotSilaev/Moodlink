import sys
sys.path.append('../..')

from database.clickhouse import client as clickhouse_client


def setAlertLevel(user_id: int, new_alert_level: int) -> None:
    alert_level, row_status = getAlertLevel(user_id, return_row_status=True)

    if not isinstance(new_alert_level, int):
        raise ValueError('new_alert_level has to be an integer.')

    match row_status:
        case 'Exists':
            query = '''
                INSERT INTO alerts (user_id, alert_level, version)
                SELECT {user_id}, {alert_level}, MAX(version) + 1
                FROM alerts
                WHERE user_id = {user_id}
            '''
        case 'DoesNotExist':
            query = '''
                INSERT INTO alerts (user_id, alert_level, version) VALUES ({user_id}, {alert_level}, 0)
            '''
        
    clickhouse_client.command(query.format(
        user_id=user_id,
        alert_level=new_alert_level,
    ))


def getAlertLevel(user_id: int, return_row_status: bool = False) -> int | tuple[int, str]:
    query = '''
        SELECT alert_level 
        FROM alerts 
        WHERE user_id = {user_id}
    '''
    rows = clickhouse_client.query(query.format(user_id=user_id)).result_rows

    if rows:
        alert_level = rows[0][0]
        row_status = 'Exists'
    else:
        alert_level = 0
        row_status = 'DoesNotExist'

    if return_row_status:
        return alert_level, row_status
    return alert_level