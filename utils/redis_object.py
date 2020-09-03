import aioredis
from utils.constants import TEST, TEST_REDIS_URL, REDIS_URL, REDIS_DB, REDIS_PWD

redis = None


async def redis_connection():
    if TEST:
        redis_db = await aioredis.create_redis_pool(TEST_REDIS_URL)
    else:
        redis_db = await aioredis.create_redis_pool(REDIS_URL,
                                                    db=REDIS_DB, password=REDIS_PWD)
    return redis_db
