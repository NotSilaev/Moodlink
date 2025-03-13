from index.values import getIndexValuesByPeriod

import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import uuid


def getIndexMeta(index_value: int) -> tuple:
    '''Provides a text description and emoji-status of the index based on its value.'''

    if index_value in range(0, 41):
        index_title = 'страх'
        index_emoji_status = '🔴'
    elif index_value in range(41, 61):
        index_title = 'нейтралитет'
        index_emoji_status = '🟡'
    elif index_value in range(61, 101):
        index_title = 'жадность'
        index_emoji_status = '🟢'

    return (index_title, index_emoji_status)


def makeIndexHistoryGraphImage(time_points: tuple, index_points: tuple) -> Path:
    '''Creates an image of the index movement graph 
    and saves it in a local directory on the same level as the importer file.
    
    :param time_points: points of hours on a graph.
    :param index_points: points of index values on a graph.
    '''

    image_uuid = uuid.uuid4()
    file_path = Path(fr'graph_images\{image_uuid}.jpg')
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        fig, ax = plt.subplots()

        ax.set_xlabel('Время (в часах)')
        ax.set_ylabel('Индекс')
        ax.grid(linestyle='-', linewidth=1)

        ax.plot(time_points, index_points)

        plt.savefig(file_path)
        plt.close(fig)

    return file_path