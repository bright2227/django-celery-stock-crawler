import redis

pool = redis.ConnectionPool(host='redis', port=6379, decode_responses=True)
re = redis.Redis(connection_pool=pool)

def run():
    re.delete('api_list')
    print('add scraper, ant, bee, non to redis')
    re.rpush('api_list', *['scraper', 'ant', 'bee', 'non'])
