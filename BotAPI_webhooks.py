import utils.redis_object as red
from fastapi import FastAPI, Request
from bot_inout import BotInput, BotOutput, BotUpdate, FormUpdate
from telegram_bot import TelegramBot
from utils.redis_object import redis_connection
from datetime import datetime
import uvicorn
import json
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

app = FastAPI(title="UBIDOTS Telegram API for Bots",
              description="Here's our API to handle creating,updating,"
                          " retrieving info and deleting bots",
              version="1.0")


@app.on_event('startup')
async def connect_redis():
    red.redis = await redis_connection()


async def redis_save(key, value):
    if key is not None and value is not None:
        await red.redis.set(json.dumps(key), json.dumps(value))


async def redis_load(key):
    if key is None:
        return None
    return json.loads(await red.redis.get(key))


@app.on_event('shutdown')
async def disconnect_redis():
    red.redis.close()
    await red.redis.await_closed()


@app.post("/api/bots/", summary="Creates a bot",
          description="Allows the creation of certain BOT after it was created at BotFather", strict_slashes=False)
async def create_bot(bot_input: BotInput):
    """
    Creates a bot webhook setting, by default the status is settled to RUN
        :param bot_input: Class that represent the correct structure for Bot Creation
        :return: Output Object that represents the Bot Created
    """
    # Setting Webhook
    parameters = {'token_bot': bot_input.token_bot, 'dataplugin_id': bot_input.dataplugin_id}

    webhook_state = await TelegramBot.init_webhook(parameters)

    # Parse info to object Class created
    dict_bot = await bot_input.to_dict()
    bot = BotOutput(**dict_bot)
    bot_dict = await bot.to_dict()

    # Save data in redis with dataplugin_id as key
    del bot_dict["dataplugin_id"]
    await redis_save(bot.dataplugin_id, bot_dict)

    return {"Bot Info": bot, "Webhook state": webhook_state}


@app.post("/api/bots/{dataplugin_id}", summary="Webhook chat bot",
          description="Allows the interaction between users and bots")
async def bot_webhook(request: Request, dataplugin_id: int):
    """
    Webhook for handling messages that comes from each bot settled at redis
        :param request: request that come as HTTP POST from Telegram API
        :param dataplugin_id: Key registered for each bot created

    :return: Status: Ok if everything goes as expected otherwise send Error
    """

    # Load data from dataplugin_id as key
    bot_data = await redis_load(dataplugin_id)
    token_bot = bot_data.get("token_bot")

    # Data that comes from Telegram API
    data = await request.json()

    # Instance for parsing and making actions
    bot = TelegramBot()
    await bot.parse_webhook_data(data)
    await bot.action(token_bot)

    return {"status": "OK"}


@app.get("/api/bots/{dataplugin_id}", summary="Info of Bot that's created",
         description="Get information of certain bot with dataplugin_id for accessing to database")
async def get_bot(dataplugin_id: int):
    """
    Retrieves the entire information of certain bot specified by it's plugin

        :param dataplugin_id: Key registered for each bot created

    :return: bot_data as the set of information for that bot
    """
    bot_data = await redis_load(dataplugin_id)
    return {"Bot Info": bot_data}


async def webhook_action(status_action, parameters):
    """
    """
    if status_action == 'RUN':

        webhook_state = await TelegramBot.init_webhook(parameters)

        bot = BotUpdate(**parameters['bot_data'])
        bot.updated_at = datetime.now()
        bot.status = status_action
        bot_dict = await bot.to_dict()

        # Save data in redis with dataplugin_id as key

        await redis_save(parameters['dataplugin_id'], bot_dict)

    elif status_action == 'PAUSE':

        webhook_state = await TelegramBot.delete_webhook(parameters)

        bot = BotUpdate(**parameters['bot_data'])
        bot.updated_at = datetime.now()
        bot.status = status_action
        bot_dict = await bot.to_dict()

        # Save data in redis with dataplugin_id as key

        await redis_save(parameters['dataplugin_id'], bot_dict)
    elif status_action == 'INFO':

        webhook_state = await TelegramBot.info_webhook(parameters)
    else:
        webhook_state = await TelegramBot.webhook_default()

    return webhook_state


@app.put("/api/bots/", summary="Updates Bot info",
         description="Modify and Updates specific features of Bot, the main objective"
                     "is giving the user the hability of STOPS and RUN the bot", strict_slashes=False)
async def update_bot(form_update: FormUpdate):
    parameters = {}

    status_action = form_update.status
    dataplugin_id = form_update.dataplugin_id

    bot_data = await redis_load(dataplugin_id)

    parameters['token_bot'] = bot_data["token_bot"]
    parameters['dataplugin_id'] = dataplugin_id
    parameters['bot_data'] = bot_data

    webhook_state = await webhook_action(status_action, parameters)
    bot_updated_data = await redis_load(dataplugin_id)

    return {"Webhook Bot State": webhook_state, 'Bot Info Updated': bot_updated_data}


@app.delete("/api/bots/", summary="Deletes Bot",
            description="Delete the entire information that belongs to a given bot by its dataplugin_id")
async def delete_bot():
    pass

if __name__ == "__main__":
    uvicorn.run("BotAPI_webhooks:app", host="127.0.0.1", port=5000, log_level="info")
