from .useragent import agents
import random
 
class ProcessHeaderMidware():
    """process request add request info"""
 
    def process_request(self, request, spider):
        ua = random.choice(agents)
        spider.logger.info(msg='now entring download midware')
        if ua:
            request.headers['User-Agent'] = ua
            # Add desired logging message here.
            spider.logger.info(
                u'User-Agent is : {} {}'.format(request.headers.get('User-Agent'), request)
            )
        pass