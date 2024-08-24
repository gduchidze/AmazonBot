from app.utils.redis_client import RedisClient

redis_client = RedisClient()
redis_client.set('test_key', 'It works!')
value = redis_client.get('test_key')
print(value)  # Should print b'It works!'