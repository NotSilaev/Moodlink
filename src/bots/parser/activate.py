"""
Script for registration and activation of a technical telegram account for the work of a bot parser.
"""

import sys
sys.path.append('../..')

from bots.parser.main import session_name, api_hash, api_id, phone_number

from telethon.sync import TelegramClient
import time


client = TelegramClient(session_name, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone_number)

code = input('Code: ')
username = input('Username: ')

time.sleep(20)
client.sign_up(code, username)
client.disconnect()