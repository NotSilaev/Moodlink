import sys
sys.path.append('../..')

from config import settings
from logs import addLog


from index.messages import getMessagesMood
from database.clickhouse import client as clickhouse_client

from telethon.tl.types import User
from telethon.tl.patched import Message

import re
import datetime


async def processMessage(user: User, message: Message) -> None:
    '''Processes message before sending them to the AI. 
       Filters out the irrelevant ones and saves the appropriate ones to the database.'''
    
    if isMessageRelevant(user, message):
        message_text: str = await removeMessageJunk(message.text)

        await saveMessageInDatabase(user, message)


async def isMessageRelevant(user: User, message: Message) -> bool:
    '''Checks the relevance of the message. 
       Filters out scams and messages that do not correspond to the subject.'''

    # 1st checking layer
    if (
        sender.username is None # User doesn't have a username
        or user.bot # User is a bot
        or user.deleted # User is deleted
        or user.scam # User has a "SCAM" marker
        or user.fake # User has a "FAKE" marker
        or len(message.text) < 10 # Too small messages
        or (not re.search(r'[a-zA-Zа-яА-Я]', message.text)) # Message doesn't have any letters
    ):
        return False

    # 2nd checking layer
    fraudulent_keywords = settings.telegram_messages_fraudulent_keywords
    for keyword in fraudulent_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            return False

    return True


async def removeMessageJunk(message_text: str) -> str:
    '''Removes all unnecessary content from the message (junk): URLs, special characters.'''

    # Remove URLs
    url_pattern = r'http[s]?://\S+|www\.\S+'
    message_text = re.sub(url_pattern, '', message_text)

    # Remove special characters
    message_text = re.sub(r'[^a-zA-Z0-9а-яА-Я0-9\s]', '', message_text)

    return message_text


async def saveMessageInDatabase(user: User, message: Message) -> None:
    user_id = user.id
    username = user.usernamet
    text = message.text
    sent_at = message.date

    try:
        query = '''
            INSERT INTO messages (user_id, username, text, sent_at, version) 
            VALUES ({user_id}, {username}, {text}, {send_at}, 0)
        '''
        clickhouse_client.command(query.format(
            user_id, username, text, sent_at
        ))

    except Exception as e:
        await addLog(
            level='CRITICAL',
            text=f"Messages aren't saved in database: {str(e)}"
        )