import sys
sys.path.append('../../')

from logs import addLog

from index.values import getLastIndexUpdates, getIndexValuesByPeriod


async def getIndex(period: tuple = None) -> dict | list:
    if not period:
        return getLastIndexUpdates()[0]
    
    return getIndexValuesByPeriod(period)
