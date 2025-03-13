from aiogram.types.user import User

import datetime


def makeGreetingMessage() -> str:
    '''Generates a welcome message based on the current time of day.'''

    hour = datetime.datetime.now().hour

    if hour in range(0, 3+1) or hour in range(22, 23+1): # 22:00 - 3:00 is night
        greeting = '🌙 Доброй ночи'
    elif hour in range(4, 11+1): # 4:00 - 11:00 is morning
        greeting = '☕️ Доброе утро'
    elif hour in range(12, 17+1): # 12:00 - 17:00 is afternoon
        greeting = '☀️ Добрый день'
    elif hour in range(18, 21+1): # 18:00 - 21:00 is evening
        greeting = '🌆 Добрый вечер'
    else:
        greeting = '👋 Доброго времени суток'
    
    return greeting


def getUserName(user: User) -> str:
    '''Generates a string to address the user.
    
    :param user: the user's aiogram object.
    '''

    user_id: int = user.id
    username: str = user.username
    first_name: str = user.first_name
    last_name: str = user.last_name
    
    if first_name:
        if last_name:
            user_name = f'{first_name} {last_name}'
        else:
            user_name = first_name
    elif username:
        user_name = f'@{username}'
    else:
        user_name = f'пользователь №{user_id}'

    return user_name


def makeCleanTimestamp(timestamp: datetime.datetime) -> str:
    '''Translates datetime into a string of a form: "yyyy-mm-dd HH:MM".'''
    
    return f"{timestamp.date()} {timestamp.hour}:{timestamp.minute}"