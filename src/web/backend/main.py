from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime

from index_api import getIndex


app = FastAPI()


@app.get("/index/latest")
async def getLatestIndex():
    index_data: dict = await getIndex()
    value = index_data['value']
    updated_at = index_data['updated_at']

    response = {
        'value': value,
        'updated_at': updated_at,
    }
    return response


@app.get("/index/period")
async def getIndexByPeriod(start_date: str, end_date: str):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    period = (start_date, end_date)

    index_values: list = await getIndex(period=period)

    response = {'index_values': index_values}
    return response
