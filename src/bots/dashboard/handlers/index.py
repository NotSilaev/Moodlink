import sys
sys.path.append('../../../')

from bots.dashboard.utils import makeCleanTimestamp
from bots.dashboard.alerts import setAlertLevel, getAlertLevel

from index.values import getLastIndexUpdates, getIndexValuesByPeriod
from index.utils import getIndexMeta, makeIndexHistoryGraphImage

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import datetime
from textwrap import dedent
from pathlib import Path
import os


router = Router(name=__name__)


@router.message(Command('index'))
@router.callback_query(F.data == 'index')
async def command_index(event: Message | CallbackQuery) -> None:
    last_index_update: dict = getLastIndexUpdates()[0]
    index_value = last_index_update['value']
    index_updated_at: datetime.datetime | None = last_index_update['updated_at']
    if index_updated_at:
        clean_index_updated_at: str = makeCleanTimestamp(index_updated_at)
    else:
        clean_index_updated_at = 'индекс ещё ни разу не обновлялся'
    index_title, index_emoji = getIndexMeta(index_value)
    
    message_text = dedent(f'''
        <b>📊 Индекс страха и жадности</b>

        {index_emoji} Показатель индекса: <b>{index_value} <i>({index_title})</i></b>

        📅 Последнее обновление: <b>{clean_index_updated_at}</b>
    ''')

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='📈 График индекса', callback_data='history')
    keyboard.button(text='🏠 В главное меню', callback_data='start')
    keyboard.adjust(1)

    kwargs = {
        'text': message_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard.as_markup(),
    }

    if isinstance(event, Message):
        await event.answer(**kwargs)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(**kwargs)
        await event.answer()


@router.message(Command('history'))
@router.callback_query(F.data == 'history')
async def command_history(event: Message | CallbackQuery) -> None:
    now = datetime.datetime.now()
    start_timestamp = now - datetime.timedelta(hours=24)
    end_timestamp = now
    clean_start_timestamp: str = makeCleanTimestamp(start_timestamp)
    clean_end_timestamp: str = makeCleanTimestamp(end_timestamp)
    period = (start_timestamp, end_timestamp)

    index_period_values: dict = getIndexValuesByPeriod(period)
    if index_period_values:
        graph_created = True

        time_points: list[str] = [updated_at.hour for updated_at in index_period_values.keys()]
        index_points: list[int] = index_period_values.values()

        index_history_graph_image_path: Path = makeIndexHistoryGraphImage(time_points, index_points)
        index_history_graph_image = FSInputFile(str(index_history_graph_image_path))

        caption_text = dedent(f'''
            *📈 График движения индекса за последние 24 часа*

            ⏰ Сформировано за период: с *{clean_start_timestamp}* до *{clean_end_timestamp}*
        ''')

        kwargs = {
            'photo': index_history_graph_image,
            'caption': caption_text,
            'parse_mode': 'Markdown'
        }
    else:
        graph_created = False
        kwargs = {
            'text': '*📂 Индекс ещё ни разу не обновлялся.*',
            'parse_mode': 'Markdown'
        }

    if isinstance(event, Message):
        event_message = event
    elif isinstance(event, CallbackQuery):
        event_message = event.message
        await event.answer()

    if graph_created:
        message = await event_message.answer_photo(**kwargs)
        # Remove graph image
        if message and index_history_graph_image_path.exists():
            os.remove(index_history_graph_image_path)
    else:
        message = await event_message.answer(**kwargs)


@router.message(Command('alerts'))
@router.callback_query(F.data == 'alerts')
async def command_alerts(event: Message | CallbackQuery) -> None:
    user_id = event.from_user.id
    alert_level: int = getAlertLevel(user_id)

    if alert_level > 0:
        base_message_text = dedent(f'''
            *🔔 Оповещения о скачках индекса*

            📊 Текущий порог: *{alert_level} пп.* (изменить: `/alerts <кол-во пунктов>`)

            💡 В случае, если индекс изменится на {alert_level} или более пунктов - Вам будет отправлено оповещение.
        ''')
    else:
        base_message_text = dedent(f'''
            *🔕 Оповещения о скачках индекса (отключены)*

            💡 Включить оповещения: `/alerts <кол-во пунктов>`
        ''')

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='🏠 В главное меню', callback_data='start')

    if isinstance(event, Message):
        message_text = event.text
        if len(message_parts := message_text.split()) > 1:
            alert_level = message_parts[1]

            if alert_level.isnumeric():
                alert_level = int(alert_level)

                if alert_level > 100:
                    message_text = '*❌ Порог не может быть больше 100 пунктов*'
                else:
                    setAlertLevel(user_id, alert_level)

                    if alert_level > 0:
                        message_text = dedent(f'''
                            *✅ Порог оповещения обновлён*

                            Теперь оповщения будут приходить, когда индекс изменится на *{alert_level}* 
                            или более пунктов.

                            💡 Отключить оповещения: `/alerts 0`
                        ''')
                    else:
                        message_text = '*🔕 Оповещения о скачках индекса отключены.*'

            else:
                message_text = dedent(f'''
                    *❌ Не удалось обновить порог оповещения*

                    Количество пунктов должно быть целым числом.

                    💡 Для установки нового порога, введите: `/alerts <кол-во пунктов>`
                ''')
        else:
            message_text = base_message_text

        await event.answer(
            text=message_text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup(),
        )

    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=base_message_text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup(),
        )
        await event.answer()
