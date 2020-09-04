from utils.constants import telegram_receiver, telegram_sender, \
    telegram_delete_webhook, telegram_webhook_info, \
    CHECK_USER_UBIDOTS
import requests_async as requests
from utils.constants import redis_load, redis_save
from bot_inout import BotUpdate
from datetime import datetime
import re
import json


# CREDITS from line 9:51 https://github.com/eternnoir/pyTelegramBotAPI/blob/master/telebot/util.py

async def is_command(text):
    """
    Checks if `text` is a command. Telegram chat commands start with the '/' character.
    :param text: Text to check.
    :return: True if `text` is a command, else False.
    """
    if text is None:
        return None
    return text.startswith('/')


async def extract_command(text):
    """
    Extracts the command from `text` (minus the '/') if `text` is a command (see is_command).
    If `text` is not a command, this function returns None.
    Examples:
    extract_command('/help'): 'help'
    extract_command('/help@BotName'): 'help'
    extract_command('/search black eyed peas'): 'search'
    extract_command('Good day to you'): None
    :param text: String to extract the command from
    :return: the command if `text` is a command (according to is_command), else None.
    """
    if text is None:
        return None
    return text.split()[0].split('@')[0][1:] if await is_command(text) else None


async def extract_arguments(text):
    """
    Returns the argument after the command.

    Examples:
    extract_arguments("/get name"): 'name'
    extract_arguments("/get"): ''
    extract_arguments("/get@botName name"): 'name'

    :param text: String to extract the arguments from a command
    :return: the arguments if `text` is a command (according to is_command), else None.
    """
    regexp = re.compile(r"/\w*(@\w*)*\s*([\s\S]*)", re.IGNORECASE)
    result = regexp.match(text)
    return result.group(2) if await is_command(text) else None


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

        if data.get('message'):
            message = data['message']
        else:
            message = data['edited_message']

        self.chat_id = message['chat']['id']
        self.incoming_message_text = message['text']
        self.first_name = message['from']['first_name']
        # self.last_name = message['from']['last_name']

    async def action(self, token_bot: str, dataplugin_id) -> bool:
        """
        Conditional actions based on set webhook data.

        Args:
            token_bot: Token that comes from bot father creation

        Returns:
            bool: True if the action was completed successfully else false
        """
        # command description used in the "help" command
        commands = {
            'token': ' type it followed by your ubidots account\'s token',
            'devices': 'List all devices at your account',
            'variables': 'type it followed by the device label in order to retrieve the variables',
        }

        success = None

        self.token_bot = token_bot

        command = await extract_command(self.incoming_message_text)

        if command == 'start':
            welcome_text = "Welcome {}! What can this bot do? \n"
            welcome_text += "- List your Devices \n"
            welcome_text += "- List your Variables \n"
            welcome_text += "- Query the last value of your variables \n"
            welcome_text += "To begin, type /token followed by your ubidots account\'s token. \n"
            self.outgoing_message_text = welcome_text.format(self.first_name)
            success = await self.send_message()

        if command == 'help':
            help_text = "The following commands are available: \n"
            for key in commands:  # generate help text out of the commands dictionary defined above
                help_text += "/" + key + ": "
                help_text += commands[key] + "\n"
            self.outgoing_message_text = help_text
            success = await self.send_message()

        if command == 'token':
            args = await extract_arguments(self.incoming_message_text)
            ubidots_token = args
            req = await requests.get(CHECK_USER_UBIDOTS.format(ubidots_token))
            if req.status_code == 200:
                bot_data = await redis_load(dataplugin_id)
                bot = BotUpdate(**bot_data)

                bot.ubidots_token = ubidots_token
                bot.updated_at = datetime.now()
                bot_dict = await bot.to_dict()
                await redis_save(dataplugin_id, bot_dict)
                self.outgoing_message_text = "Thank You {}!, now you are logged in".format(self.first_name)
            else:
                self.outgoing_message_text = "Oops, something went wrong with the authentication {}," \
                                             " the app returned {}" \
                    .format(self.first_name, req.status_code)
            success = await self.send_message()

        if command == 'devices':
            bot_data = await redis_load(dataplugin_id)
            ubidots_token = bot_data.get("ubidots_token")
            endpoint = "industrial.api.ubidots.com"
            url = "https://{}/api/v2.0/devices/".format(endpoint)

            headers = {"X-Auth-Token": ubidots_token}
            req = await requests.get(url=url, headers=headers)
            devices = []

            req_dict = json.loads(req.text)
            n_devices = req_dict.get('count')
            devices_list = req_dict.get('results')

            for device in range(0, n_devices, 1):
                devices.append(devices_list[device].get('label'))

            devices_msg = "Here is the list of your devices with their labels: \n "
            counter = 0
            for device in devices:
                counter += 1
                devices_msg += "/{}. {} \n".format(counter, device)

            self.outgoing_message_text = devices_msg

            success = await self.send_message()

        if command == 'ping':
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
