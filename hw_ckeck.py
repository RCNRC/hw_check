from time import sleep
import logging
import sys
import requests
from dotenv import dotenv_values
import telegram


class MyLogsHandler(logging.Handler):

    def __init__(
            self,
            tg_bot_logger: telegram.Bot,
            tg_bot: telegram.Bot,
            chat_id,
    ):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot_logger = tg_bot_logger
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot_logger.send_message(chat_id=self.chat_id, text=log_entry)
        if record.levelname == 'DEBUG':
            self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    logging.basicConfig(
        format='%(process)d[%(levelname)s](%(asctime)s): %(message)s',
    )
    logger = logging.getLogger("Логгер бота.")
    logger.setLevel(logging.DEBUG)
    devman_api_token = dotenv_values('.env')['DEVMAN_API_TOKEN']
    bot_telegram_api_token = dotenv_values('.env')['TELEGRAM_BOT_API_TOKEN']
    bot_telegram_logger_api_token = dotenv_values('.env')[
        'TELEGRAM_BOT_LOGGER_API_TOKEN'
    ]
    chat_id = dotenv_values('.env')['TELEGRAM_CHAT_ID']
    logger.addHandler(MyLogsHandler(
        telegram.Bot(token=bot_telegram_logger_api_token),
        telegram.Bot(token=bot_telegram_api_token),
        chat_id,
    ))
    headers = {
        'Authorization': f'Token {devman_api_token}'
    }
    params = {}
    base_url = 'https://dvmn.org/api/'
    request_timeout = 120
    long_polling_api_endpoint = 'long_polling/'
    logger.info('Bot started successfully.')
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
                    logger.debug(text)
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
            logger.warning('Connection was terminated unexpectedly.')
            sleep(request_timeout)
        except KeyboardInterrupt:
            logger.info('Bot ended work.')
            sys.exit(0)
        except Exception as exception:
            logger.exception(exception)


if __name__ == '__main__':
    main()
