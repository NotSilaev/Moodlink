import sys
sys.path.append('..')

from logs import addLog

from index.messages import setMoodForUnclassifiedMessages, getMessagesWithMood
from index.values import setIndexValue, getLastIndexUpdates
from index.alerts import sendAlert

from database.clickhouse import client as clickhouse_client

import datetime
import asyncio
from textwrap import dedent


async def calculateIndex() -> None:
    '''Calculates the index based on the messages saved in the last hour.'''

    await addLog(
        level='INFO',
        text=f"Index calculation started."
    )

    now = datetime.datetime.now().replace(microsecond=0)
    start_date = now - datetime.timedelta(hours=1)
    end_date = now

    await setMoodForUnclassifiedMessages(start_date, end_date) # Analyzing all unclassified messages
    messages_mood_rows = await getMessagesWithMood(start_date, end_date) # Receiving all classified messages

    moods = {
        'greed': 0,
        'fear': 0,
        'neutral': 0,
    }

    last_index = getLastIndexUpdates()[0]['value']

    if messages_mood_rows:
        total_messages = 0
        for row in messages_mood_rows:
            mood = row[0].lower()
            if mood == 'null': 
                continue
            moods[mood] += 1
            total_messages += 1
        index = int(50 + ((moods['greed'] - moods['fear']) / total_messages) * 50)
    else:
        index = last_index

    index_change = index - last_index

    await setIndexValue(
        value=index, 
        greed_msg_count=moods['greed'], 
        fear_msg_count=moods['fear'], 
        neutral_msg_count=moods['neutral'],
        updated_at=now
    )

    await addLog(
        level='INFO',
        text=dedent(f'''
            Index calculation finished.

            Last index value: {last_index}
            New index value: {index} ({index_change})
            Messages processed: {total_messages}
            
            Greed: {moods["greed"]}
            Fear: {moods["fear"]}
            Neutral: {moods["neutral"]}
        ''')
    )

    await sendAlert(index, abs(index_change))


if __name__ == '__main__':
    asyncio.run(calculateIndex())