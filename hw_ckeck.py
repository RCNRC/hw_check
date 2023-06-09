import json
import time
import sys
import requests
from dotenv import dotenv_values
import telegram


def main():    
    devman_api_token = dotenv_values('.env')['DEVMAN_API_TOKEN']
    bot_legram_api_token = dotenv_values('.env')['TELEGRAM_BOT_API_TOKEN']
    chat_id = dotenv_values('.env')['TELEGRAM_CHAT_ID']
    bot = telegram.Bot(token=bot_legram_api_token)

    headers = {
        'Authorization': f'Token {devman_api_token}'
    }
    params = {}
    base_url = 'https://dvmn.org/api/'
    request_timeout = 120
    long_polling_api_endpoint = 'long_polling/'
    while True:
        try:
            response = requests.get(
                f'{base_url}{long_polling_api_endpoint}',
                headers=headers,
                params=params,
                timeout=request_timeout,
            )
            response.raise_for_status()
            attempts = response.json()
            if attempts['status'] == 'found':
                for attempt in attempts['new_attempts']:
                    text_title = f'Был проверен урок '\
                                 f'{attempt["lesson_title"]}\n\n'
                    text_body = 'Нужно доработать.\n\n'\
                                if attempt['is_negative']\
                                else 'Принято.\n\n'
                    text_end = f'Ссылка: {attempt["lesson_url"]}'
                    text = f'{text_title}{text_body}{text_end}'
                    bot.send_message(chat_id=chat_id, text=text)
                params = {
                    'timestamp': attempts['last_attempt_timestamp'],
                }
            elif attempts['status'] == 'timeout':
                params = {
                    'timestamp': attempts['timestamp_to_request'],
                }
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            print('Connection was terminated unexpectedly.')
            time.sleep(request_timeout)
        except KeyboardInterrupt:
            print('Bot ends work.')
            sys.exit(0)


if __name__ == '__main__':
    main()
