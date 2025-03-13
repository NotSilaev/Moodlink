import sys
sys.path.append('../..')

from config import settings

from bots.dashboard.handlers.index import router as index_router
from bots.dashboard.utils import makeGreetingMessage, getUserName

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from textwrap import dedent


bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


@dp.message(CommandStart())
@dp.message(F.text & (~F.text.startswith("/")))
@dp.callback_query(F.data == 'start')
async def command_start(event: Message | CallbackQuery) -> None:
    '''Bot start menu.'''

    greeting: str = makeGreetingMessage()
    user_name: str = getUserName(user=event.from_user)

    message_text = dedent(f'''
        *{greeting}*, {user_name}

        *————— Команды —————*
        • /index - текущий показатель индекса.
        • /history - график индекса за последние 24 часа.
        • /alerts - управление оповещениями.
        *———————————————*
    ''')

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='📊 Индекс', callback_data='index')
    keyboard.button(text='📈 График', callback_data='history')
    keyboard.button(text='🔔 Оповещения', callback_data='alerts')
    keyboard.adjust(2)

    kwargs = {
        'text': message_text,
        'parse_mode': 'Markdown',
        'reply_markup': keyboard.as_markup(),
    }

    if isinstance(event, Message):
        await event.answer(**kwargs)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(**kwargs)
        await event.answer()


async def main() -> None:
    dp.include_router(index_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print('Bot has been stopped.')