import utils.redis_object as red
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()


TEST = False
HEROKU = False
TEST_REDIS_URL = 'redis://localhost'
REDIS_URL = getenv('REDIS_URL')
REDIS_DB = int(getenv('REDIS_DB'))
REDIS_PWD = getenv('REDIS_PWD')
BASE_TELEGRAM_URL = 'https://api.telegram.org/bot{}'
CHECK_USER_UBIDOTS = 'http://industrial.api.ubidots.com/api/v1.6/user_check/?token={}'


async def redis_save(key: object, value: object) -> object:
    """
        Function that allows to load certain value from Redis Database

    :param key: Our redis Key that stores each element by its dataplugin_id
    :param value: Our values to be stored

        {created_at:'', updated_at:'',
        status: '', owner_id: '', token_bot:'', ubidots_token:''}

    :return: object
    """
    if key is not None and value is not None:
        await red.redis.set(json.dumps(key), json.dumps(value))


async def redis_load(key: object) -> object:
    """
        Function that allows to load certain value from Redis Database

    :param key: Our redis Key that stores each element by its dataplugin_id

    :return: object
    """
    if key is None:
        return None
    value = await red.redis.get(key)
    if value is not None:
        return json.loads(value)
    return "error, dataplugin_id is not related to any bot"


# TELEGRAM RECEIVER

async def telegram_receiver(token: str, dataplugin_id: str) -> str:
    """
        Function that allows to set the Webhook URL for receiving UPDATES
        from telegram server

    :param token: str:
    :param dataplugin_id:
    :return: URL string that represents which patch in our API receives UPDATES
    """

    if HEROKU:
        HEROKU_URL = 'https://jconnor-ubidots-bots.herokuapp.com'
        WEBHOOK_ENDPOINT = HEROKU_URL + '/api/bots/{}'.format(dataplugin_id)
    else:
        NGROK_URL = 'https://674f7fe475cf.ngrok.io'
        WEBHOOK_ENDPOINT = NGROK_URL + '/api/bots/{}'.format(dataplugin_id)

    TELEGRAM_INIT_WEBHOOK_URL = BASE_TELEGRAM_URL.format(token) + '/setWebhook?url=' + WEBHOOK_ENDPOINT
    return TELEGRAM_INIT_WEBHOOK_URL


async def telegram_sender(token: str, chat_id: int, text: str) -> str:
    """
        Function that allows to send message based in chat_id and token_bot
        replies with text

    :param token: Telegram bot Token
    :param chat_id: Chat ID of Telegram chat, used to identify which conversation
                    outgoing messages should be send to.
    :param text: Text of Telegram chat
    :return: URL string that represents where to send messages
    """
    TELEGRAM_SEND_MESSAGE_URL = BASE_TELEGRAM_URL.format(token) + '/sendMessage?chat_id={}&text={}'.format(chat_id, text)
    return TELEGRAM_SEND_MESSAGE_URL


async def telegram_webhook_info(token: str) -> str:
    """
        Function that allows to see entire information about the
        Webhook that was set

    :param token: Telegram bot Token
    :return: URL string that represents the entire Webhook INFO
    """
    TELEGRAM_WEBHOOK_INFO_URL = BASE_TELEGRAM_URL.format(token) + '/getWebhookInfo'
    return TELEGRAM_WEBHOOK_INFO_URL


async def telegram_delete_webhook(token: str) -> str:
    """
        Function that allows to delete from telegram server
        Webhooks from specified bot

    :param token: Telegram bot Token
    :return: URL string that represents where to delete the specified Webhook
    """
    TELEGRAM_WEBHOOK_DELETE_URL = BASE_TELEGRAM_URL.format(token) + '/deleteWebhook'
    return TELEGRAM_WEBHOOK_DELETE_URL
