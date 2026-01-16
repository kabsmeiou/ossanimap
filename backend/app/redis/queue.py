from redis import Redis
from rq import Queue

redis_conn = Redis(host="localhost", port=6379)
pack_creation_queue = Queue(
    "pack_queue", 
    connection=redis_conn, 
    default_timeout=600
)