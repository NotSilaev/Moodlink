import requests


async def telegramAPIRequest(bot_token: str, request_method: str, api_method: str, parameters:dict={}) -> str:
    '''Sends request to Telegram API.

    :param bot_token: the token of the bot that the request is coming from.
    :param request_method: http request method (`GET` or `POST`).
    :param api_method: the required method in Telegram API.
    :param parameters: dict of parameters which will used in the Telegram API method.
    '''

    request = f"https://api.telegram.org/bot{bot_token}/{api_method}?{'&'.join([f'{k}={v}' for k, v in parameters.items()])}"

    if request_method == 'GET':
        r = requests.get(request)
    elif request_method == 'POST':
        r = requests.post(request)
    else:
        raise ValueError('Unavailable request method.')

    response = {
        'code': r.status_code,
        'text': r.text,
    }
    
    return response