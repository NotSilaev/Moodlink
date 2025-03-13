import sys
sys.path.append('..')

from logs import addLog

from api.chatgpt import sendPromtMessages

from database.clickhouse import client as clickhouse_client

import ast
import datetime


async def getMessagesMood(messages: list) -> list:
    '''Sends a message to AI and gets one of three moods in response: fear, neutrality, or greed.'''

    promt_messages = [
        {
            'role': 'system',
            'content': f'''
                Classify the investment sentiment of each text as Fear, Greed, Neutral, or NULL (if not related to crypto). 
                Respond with an array of single-word classifications: Fear/Greed/Neutral/NULL (in English). 
                Fear: panic, anxiety, drop expectation, sell desire. Example: биток летит на дно, я потерял деньги
                Greed: confidence, FOMO, growth expectation, buy desire. Example: биток 100К скоро, это ракета
                Neutral: facts, technical analysis. Example: BTC стоит 50000
                NULL: unrelated to crypto. Example: пойду в кино
            '''
        },
        {
            'role': 'user', 
            'content': f'Texts: {messages}'
        },
    ]

    max_output_tokens = len(messages) * 10 # 10 tokens for each message
    ai_response = await sendPromtMessages(messages=promt_messages, max_tokens=max_output_tokens)
    messages_mood = ast.literal_eval(ai_response.content) # content str to list
    
    return messages_mood


async def setMoodForUnclassifiedMessages(start_date: datetime.datetime, end_date: datetime.datetime) -> None:
    '''Receives all untagged messages in the specified time range and runs them through the AI to get the mood.'''

    # Get messages in period
    query = '''
        SELECT id, user_id, username, text, sent_at, version
        FROM messages 
        WHERE 
            mood IS NULL
            AND (sent_at BETWEEN '{start_date}' AND '{end_date}')
    '''
    messages = clickhouse_client.query(query.format(
        start_date=start_date, 
        end_date=end_date
    )).result_rows

    if not messages:
        await addLog(level='INFO', text="No messages to update mood for.")
        return

    # Get each message mood
    messages_text = [msg[3] for msg in messages]
    messages_mood: list = await getMessagesMood(messages=messages_text)

    # Update messages mood in database
    messages_id = ' ,'.join([str(msg[0]) for msg in messages])
    delete_query = f'ALTER TABLE messages DELETE WHERE id IN ({messages_id})'
    optimize_query = 'OPTIMIZE TABLE messages FINAL'
    
    values = ' ,'.join([
        f"({msg[0]}, '{msg[1]}', '{msg[2]}', '{msg[3]}', '{messages_mood[i]}', '{msg[4]}', {msg[5] + 1})"
        for i, msg in enumerate(messages)
    ])
    insert_query = f'''
        INSERT INTO messages (id, user_id, username, text, mood, sent_at, version)
        VALUES {values}
    '''
    
    # Execute the query
    try:
        clickhouse_client.command(delete_query)
        clickhouse_client.command(optimize_query)
        clickhouse_client.command(insert_query)

        await addLog(
            level='INFO',
            text=f"Messages (count: {len(messages)}) mood successfully updated."
        )

    except Exception as e:
        await addLog(
            level='CRITICAL',
            text=f"Messages mood isn't updated in database: {str(e)}"
        )


async def getMessagesWithMood(start_date: datetime.datetime, end_date: datetime.datetime) -> list[str]:
    '''Returns all tagged messages in the specified time range.'''

    query = '''
        SELECT mood
        FROM messages 
        WHERE 
            mood IS NOT NULL
            AND (sent_at BETWEEN '{start_date}' AND '{end_date}')
    '''
    messages_mood = clickhouse_client.query(query.format(
        start_date=start_date, 
        end_date=end_date
    )).result_rows

    return messages_mood