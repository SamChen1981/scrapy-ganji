# -*- coding: utf-8 -*-
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from ganji.items import qianzhan_list
from ganji.mysqlpipelines.sql import Sql
from ganji.mysqlpipelines.redis import Myredis
import re
from ganji.create_table import Ganji
# from scrapy.utils.project import get_project_settings


class ShunqiDetailSpider(RedisSpider):
    city = 'eerduosi'
    name = "ganji_"+city+"_fenye"
    custom_settings = {
        'ITEM_PIPELINES':{
            'ganji.mysqlpipelines.pipelines.GanjipagePipeline': 301,
        },
        'DOWNLOAD_DELAY' : 2,
        'CONCURRENT_REQUESTS' : 1,
        'DOWNLOAD_TIMEOUT' : 10,
        "DOWNLOADER_MIDDLEWARES" : {
            'ganji.MidWare.qianzhan_proxy.ProxyMiddleware': 300,
            'ganji.MidWare.HeaderMidWare.ProcessHeaderMidware': 543,
        }
    }

    def __init__(self):
        self.start_sql = 'SELECT url,curr_page from ganji_all_cityurl WHERE url LIKE "http://'+self.city+'.%" and complete=0 LIMIT 1'
    def start_requests(self):
        # Ganji.check(self.city)
        # exit(0)
        result = Sql.start_urls(self.start_sql,'all')
        # for res in result:
        #     print(res[0])
        #     Myredis.push_url(self.name,res[0])
        yield Request(result[0][0]+'/', self.parse)
    def push_url(self, url, code):
        if re.search(r'o(\d+)',url):  #如果是分页：
            temp_url = re.search(r'o(\d+)',url).group(0)
            push_url = url.replace(temp_url+'/','')
        else :
            push_url = url
        if code==1: #如果等于1， 就把链接设置为已采集完成，并push新链接
            print(push_url[0:-1])
            Sql.change_status('update ganji_all_cityurl set complete=1 where url=%s',push_url[0:-1])
            result = Sql.start_urls(self.start_sql,'all')
            Myredis.push_url(self.name,result[0][0]+'/')
        else:
            Myredis.push_url(self.name,push_url)
    handle_httpstatus_list = range(300,600)
    def parse(self, response):
        # 目前只采集一页
        #状态码：
        # 1，采集完成
        self.logger.info('now you can see the url %s' % response.url)
        # print(response.body)
        if  response.status==200 and response.xpath("//div[@class='txt']/p") :
            numbers = ''.join(response.xpath("//span[contains(text(),'赶集网为您找到')]/*[1]/text()").extract()).replace('条','')
            # 翻页  如果下一页地址等于空，则到达最后一页进行翻页
            if response.xpath("//div[@class='pageBox']//a") :  #如果有页码，则检查有无下一页按钮
                if response.xpath("//span[text()='下一页']"):  #如果有下一页
                    nextpage = response.xpath("//span[text()='下一页']/parent::a/@href").extract()[0]
                    if int(re.findall(r"/o(.+?)/",nextpage)[0]) >= 34: #如果页码大于34，则采集完成
                        self.push_url(response.url,1)
                    else:  #否则跳转下一页
                        Myredis.push_url(self.name,'http://'+self.city+'.ganji.com'+nextpage)
                else:
                    self.push_url(response.url,1) #如果没有下一页，则采集完成
            elif int(numbers) > 49:#如果条数太多不显示页面，强制跳转到第二页
                Myredis.push_url(self.name,response.url+'o2/')
            else: # 如果就一页则采集完成
                self.push_url(response.url,1)
            a_item = response.xpath("//div[@class='txt']/p[1]/a[1]")
            # self.push_url(response.url,1)
            item = qianzhan_list()
            item['url'] = []
            item['city'] = self.city
            for a in a_item:
                if (self.city not in a.xpath("@href").extract()[0]) and ('http' not in a.xpath("@href").extract()[0]):
                    item['url'].append('http://'+self.city+'.ganji.com'+a.xpath("@href").extract()[0])
                elif self.city in a.xpath("@href").extract()[0]:
                    item['url'].append('http:'+a.xpath("@href").extract()[0])
                else:
                    item['url'].append(a.xpath("@href").extract()[0])
            return item
        else: #如果没有采集到
            if response.status == 301 :
            #获取跳转前的地址，并修改数据库地址
                refferurl = bytes.decode(response.headers['Location'])
                if re.search(r'(/o[0-9])/',refferurl):  #如果是分页：
                    temp_url = re.search(r'(o[0-9])/',refferurl).group(0)
                    self.push_url(refferurl.replace(temp_url,''),1)
                else :
                    self.push_url(refferurl,1)
            elif response.status == 403:
                self.push_url(response.url,1)
            elif 'confirm' not in response.url: #如果不是验证码，则设置已完成
                self.push_url(response.url,1)
            else:
                self.push_url(response.url,1)