import sys
sys.path.append('../..')

from config import settings
from logs import addLog
from messages import processMessage

from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
import asyncio


# Telethon config
api_id: int = settings.telegram_app_api_id
api_hash: str = settings.telegram_app_api_hash
phone_number: str = settings.telegram_app_phone_number


async def subscribeToChannels(client) -> None:
    channels = settings.telegram_channels
    subscribed_channels = set()

    for channel in channels:
        if channel in subscribed_channels:
            continue

        try:
            entity = await client.get_input_entity(channel)
            await client(JoinChannelRequest(entity)) # Join channel

            # Check channel discussion group exists
            full_channel = await client(GetFullChannelRequest(entity))
            if full_channel.full_chat.linked_chat_id:
                discussion_chat = await client.get_entity(full_channel.full_chat.linked_chat_id)
                await client(JoinChannelRequest(discussion_chat)) # Join channel discussion group
    
            subscribed_channels.add(channel)

            await addLog(
                level='INFO',
                text=f"Bot subscribed to: {channel}"
            )

        except Exception as e:
            await addLog(
                level='ERROR',
                text=f"Channel ({channel}) subscription error: {str(e)}"
            )


async def listenToMessages(client) -> None:
    @client.on(events.NewMessage())
    async def handler(event):
        message = event.message

        if message.from_id and isinstance(message.from_id, PeerUser):
            try:
                user_id = message.from_id.user_id
                user = await client.get_entity(user_id)

                await processMessage(
                    user=user,
                    message=message
                )
                chat_title = getattr(event.chat, 'title', 'unknown chat')

                await addLog(
                    level='INFO',
                    text=f"New message in {chat_title}: {event.text}"
                )
            except Exception as e:
                await addLog(
                    level='ERROR',
                    text=f"Error processing message: {str(e)}"
                )


async def main() -> None:
    session_name = 'parser'
    client = TelegramClient(session_name, api_id, api_hash)

    await client.start(phone=phone_number)
    await subscribeToChannels(client)
    await listenToMessages(client)

    await client.catch_up()

    await addLog(
        level='INFO',
        text="Bot started listening to messages."
    )

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
