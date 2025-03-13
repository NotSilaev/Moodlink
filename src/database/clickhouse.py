import sys
sys.path.append('..')

from config import settings

import clickhouse_connect


client = clickhouse_connect.get_client(
    host=settings.clickhouse_host,
    user=settings.clickhouse_user,
    password=settings.clickhouse_password,
    port=settings.clickhouse_port,
    secure=settings.clickhouse_secure
)