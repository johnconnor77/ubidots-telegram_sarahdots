from utils.constants import telegram_receiver, telegram_sender, telegram_delete_webhook, telegram_webhook_info
import requests_async as requests
import json


class TelegramBot:

    def __init__(self):
        """"
        Initializes an instance of the TelegramBot class.

        Attributes:
            chat_id:str : Chat ID of Telegram chat, used to identify which conversation
                         outgoing messages should be send to.
            text:str : Text of Telegram chat
            first_name :str: First name of the user who sent the message
            last_name :str: Last name of the user who sent the message
        """

        self.chat_id = None
        self.text = None
        self.first_name = None
        self.last_name = None
        self.incoming_message_text = None
        self.token_bot = None
        self.outgoing_message_text = None

    async def parse_webhook_data(self, data: str):
        """
        Parses Telegram JSON request from webhook and sets fields for conditional actions

        Args:
            data:str: JSON string of data
        """

        message = data['message']

        self.chat_id = message['chat']['id']
        self.incoming_message_text = message['text'].lower()
        self.first_name = message['from']['first_name']
        self.last_name = message['from']['last_name']

    async def action(self, token_bot: str) -> bool:
        """
        Conditional actions based on set webhook data.

        Args:
            token_bot: Token that comes from bot father creation

        Returns:
            bool: True if the action was completed successfully else false
        """
        success = None

        self.token_bot = token_bot

        if self.incoming_message_text == '/hello':
            self.outgoing_message_text = "Hello {} {}!".format(self.first_name, self.last_name)
            success = await self.send_message()

        if self.incoming_message_text == '/ping':
            self.outgoing_message_text = '🤙pong'
            success = await self.send_message()

        return success

    async def send_message(self) -> bool:
        """
        Sends message to Telegram servers.
        """

        TELEGRAM_SEND_MESSAGE_URL = await telegram_sender(self.token_bot,
                                                          self.chat_id,
                                                          self.outgoing_message_text)

        res = await requests.post(TELEGRAM_SEND_MESSAGE_URL)
        return True if res.status_code == 200 else False

    @staticmethod
    async def webhook_default():
        raise ValueError("Non valid Action")

    @staticmethod
    async def init_webhook(parameters: dict) -> dict:
        """
        Initializes the webhook

        Args:
            parameters.token: str: Bot Token from BotFather
            parameters.dataplugin_id: id given a
        """

        token_bot = parameters.get('token_bot')
        dataplugin_id = parameters.get('dataplugin_id')

        TELEGRAM_INIT_WEBHOOK_URL = await telegram_receiver(token_bot, dataplugin_id)

        res = await requests.get(TELEGRAM_INIT_WEBHOOK_URL)

        webhook_res = {"Webhook URL": res.url,
                       "status_code": res.status_code,
                       "Content": json.loads(res.content)}

        return webhook_res

    @staticmethod
    async def delete_webhook(parameters: dict) -> dict:
        """
        Deletes the webhook

        Args:
            :parameter token: str: Bot Token from BotFather
        """

        token_bot = parameters.get('token_bot')

        TELEGRAM_WEBHOOK_DELETE_URL = await telegram_delete_webhook(token_bot)

        res = await requests.get(TELEGRAM_WEBHOOK_DELETE_URL)

        webhook_res = {"Webhook URL": res.url,
                       "status_code": res.status_code,
                       "Content": json.loads(res.content)}

        return webhook_res

    @staticmethod
    async def info_webhook(parameters: dict) -> dict:
        """
        Deletes the webhook

        Args:
            :parameter token: str: Bot Token from BotFather
        """

        token_bot = parameters.get('token_bot')

        TELEGRAM_WEBHOOK_INFO_URL = await telegram_webhook_info(token_bot)

        res = await requests.get(TELEGRAM_WEBHOOK_INFO_URL)

        webhook_res = {"Webhook URL": res.url,
                       "status_code": res.status_code,
                       "Content": json.loads(res.content)}

        return webhook_res

