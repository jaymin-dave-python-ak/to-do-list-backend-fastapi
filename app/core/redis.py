import redis 

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_redis():
    """Provide a Redis client instance for caching and blacklisting refresh tokens."""
    try:
        yield redis_client
    finally:
        pass