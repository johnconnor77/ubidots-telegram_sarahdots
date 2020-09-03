# TODO: Move to environment variables

TEST = False
TEST_REDIS_URL = 'redis://localhost'
REDIS_URL = 'redis://redis-13775.c91.us-east-1-3.ec2.cloud.redislabs.com:13775'
REDIS_DB = 0
REDIS_PWD = "9JfQOCKAdvnt16iVQDQncOi0mrzyihto"
BASE_TELEGRAM_URL = 'https://api.telegram.org/bot{}'


# TELEGRAM RECEIVER

async def telegram_receiver(token, dataplugin_id):
    NGROK_URL = 'https://6261189dbb18.ngrok.io'
    LOCAL_WEBHOOK_ENDPOINT = NGROK_URL + '/api/bots/{}'.format(dataplugin_id)
    TELEGRAM_INIT_WEBHOOK_URL = BASE_TELEGRAM_URL.format(token) + '/setWebhook?url=' + LOCAL_WEBHOOK_ENDPOINT
    return TELEGRAM_INIT_WEBHOOK_URL


# TELEGRAM SENDER

async def telegram_sender(token, chat_id, text):
    TELEGRAM_SEND_MESSAGE_URL = BASE_TELEGRAM_URL.format(token) + '/sendMessage?chat_id={}&text={}'.format(chat_id, text)
    return TELEGRAM_SEND_MESSAGE_URL


# TELEGRAM WEBHOOK INFO

async def telegram_webhook_info(token):
    TELEGRAM_WEBHOOK_INFO_URL= BASE_TELEGRAM_URL.format(token) + '/getWebhookInfo'
    return TELEGRAM_WEBHOOK_INFO_URL


# TELEGRAM DELETE WEBHOOK

async def telegram_delete_webhook(token):
    TELEGRAM_WEBHOOK_DELETE_URL = BASE_TELEGRAM_URL.format(token) + '/deleteWebhook'
    return TELEGRAM_WEBHOOK_DELETE_URL
