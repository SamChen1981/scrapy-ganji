import redis
from ganji import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

r = redis.Redis(REDIS_HOST, REDIS_PORT, db=0)

class Myredis:
    @classmethod
    def push_url(cls, spider_name, url):
        r.lpush(spider_name+':start_urls',url)    #把URLpush进redis，根据spider_name

    @classmethod
    def check_list(cls, spider_name):
        return r.llen(spider_name+':start_urls')    #把URLpush进redis，根据spider_name
        
