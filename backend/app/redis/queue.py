from redis.asyncio import Redis as AsyncRedis
from redis import Redis
from rq import Queue

redis_async = AsyncRedis(host="redis", port=6379)
redis_sync = Redis(host="redis", port=6379, decode_responses=False)

pack_creation_queue = Queue(
    "pack_queue", 
    connection=redis_sync, 
    default_timeout=600
)
