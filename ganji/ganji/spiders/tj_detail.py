# -*- coding: utf-8 -*-
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from ganji.items import qianzhan_detail
from ganji.mysqlpipelines.sql import Sql
from ganji.mysqlpipelines.redis import Myredis
import re

class QianzhanDetailSpider(RedisSpider):
    city = 'eerduosi'
    # name = "ganji_"+city+"_fenye"
    name = "ganji_"+city+"_detail"
    # allowed_domains = ["youtrip.com"]
    # start_urls = (
    #     'http://xingtai.ganji.com/fuwu_dian/918005367x/zhuzhaibanjia/',
    # )
    custom_settings = {
        'ITEM_PIPELINES':{
            'ganji.mysqlpipelines.pipelines.GanjidetailPipeline': 301,
        },
        # 'DOWNLOAD_DELAY' : 1,
        'DOWNLOAD_TIMEOUT':10,
        'CONCURRENT_REQUESTS' : 4,
        'COOKIES_ENABLED' : False,
        "DOWNLOADER_MIDDLEWARES" : {
            'ganji.MidWare.qianzhan_proxy.ProxyMiddleware': 300,
            'ganji.MidWare.HeaderMidWare.ProcessHeaderMidware': 543,
        },
        # 'HTTPCACHE_ENABLED' : True,
        # 'HTTPCACHE_EXPIRATION_SECS' : 0,
        # 'HTTPCACHE_DIR' : 'httpcache',
        # 'HTTPCACHE_IGNORE_HTTP_CODES' : [],
        # 'HTTPCACHE_STORAGE' : 'scrapy.extensions.httpcache.FilesystemCacheStorage',
    }
    def __init__(self):
        self.start_sql = 'SELECT url,id from '+self.name+' where success=0' 
    def start_requests(self):
        # for url in self.start_urls:
        #     yield Request(url, self.parse)
        result = Sql.start_urls(self.start_sql,2)
        for names in result:
            # print(names[0]+"?companyid="+str(names[1]))
            if 'javascript:' in names[0]:
                Sql.change_status("update "+self.name+" set success=2 where id=%s",names[1])
            else:
                url = self.checkurl(names[0]+"?companyid="+str(names[1]))
                yield Request(url, self.parse)
    def push_url(self, com_name, complete):
        if complete == 1:
            Sql.change_status("update "+self.name+" set success=1 where id=%s",com_name)
        elif complete == 2:
            Sql.change_status("update "+self.name+" set success=2 where id=%s",com_name)
        else:
            pass
        if(Myredis.check_list(self.name)):
            pass
        else:
            result = Sql.start_urls(self.start_sql,5)
            for names in result:
                url = self.checkurl(names[0]+"?companyid="+str(names[1]))
                if 'javascript:' in names[0]:
                    Sql.change_status("update "+self.name+" set success=2 where id=%s",names[1])
                else:
                    url = self.checkurl(names[0]+"?companyid="+str(names[1]))
                    Myredis.push_url(self.name,url)
    handle_httpstatus_list = range(300,600)
    def checkurl(self,url):
        if(len(re.findall(r'http',url)) > 1):
            return url[5:]
        else:
            return url
    def parse(self, response):
        # 目前只采集一页
        # print(response.body)
        print(response.meta)
        self.logger.info('now you can see the url %s' % response.url)
        #不存在跳转
        if (response.status==200 or response.status==304 )and ('redirect_urls' not in response.meta) and(response.xpath("//div[@class='d-top-area']")) :
            # spans = response.xpath("//article[@class='main']/preceding-sibling::article[1]")  #顶部三个主要信息
            item = qianzhan_detail()
            companyid = re.findall(r"companyid=(.+?)$",response.url)[0]
            
            if response.xpath("//h1[1]/text()").extract()[-1].split():
                item['companyname'] = ''.join(response.xpath("//h1[1]/text()").extract()[-1])
            else:
                item['companyname'] = ''.join(response.xpath("//h1[1]/text()").extract()[0])
            
            if(re.findall(r"@phone=(.+?)@",''.join(response.xpath("//a[contains(@class,'displayphonenumber')]/@gjalog").extract()))):
                item['tel'] = re.findall(r"@phone=(.+?)@",''.join(response.xpath("//a[contains(@class,'displayphonenumber')]/@gjalog").extract()))[0]
            else:
                item['tel'] = ''
            #item['tel'] = ''.join(re.findall(r"@phone=(.+?)@",''.join(response.xpath("//a[contains(@class,'displayphonenumber')]/@gjalog").extract())))
            item['address'] = ''.join(response.xpath("//span[contains(text(),'地　　址')]/following-sibling::div[1]//text()").extract())
            item['fuwutese'] = ''.join(response.xpath("//span[contains(text(),'服务特色')]/following-sibling::p/text()").extract())
            item['tigongfuwu'] = ';'.join(response.xpath("//span[contains(text(),'提供服务')]/following-sibling::p/a/text()").extract())
            item['fuwufanwei'] = ';'.join(response.xpath("//span[contains(text(),'服务范围')]/following-sibling::p/a/text()").extract())
            item['lianxiren'] = ''.join(response.xpath("//span[contains(text(),'联 系 人：')]/following-sibling::p/text()").extract())
            item['shangjiadizhi'] = ''.join(response.xpath("//span[contains(text(),'商家地址')]/following-sibling::p//text()").extract())
            item['yingyeshijian'] = ''.join(response.xpath("//span[contains(text(),'营业时间')]/following-sibling::p/text()").extract())
            item['website'] = ''.join(response.xpath("//span[contains(text(),'网  址：')]/following-sibling::p/a/text()").extract())
            item['jianjie'] = ''.join(response.xpath("//div[@class='service-about']//div[@class='txt']").extract())
            item['cate'] = ';'.join(response.xpath("//div[contains(@class,'crumbs clearfix')]//a/text()").extract())
            item['ID'] = companyid
            item['table'] = self.name
            # print(item)
            for key in item:
                if item[key].strip() == '':
                    item[key] = '无'
                else:
                    item[key] = item[key].strip() 
            yield item
                # pass
            self.push_url(companyid,3)
        #其他培训
        elif (response.status==200 or response.status==304 )and ('redirect_urls' not in response.meta) and(response.xpath("//div[@id='wrapper']//div[@class='leftbox']")) :
            # spans = response.xpath("//article[@class='main']/preceding-sibling::article[1]")  #顶部三个主要信息
            item = qianzhan_detail()
            companyid = re.findall(r"companyid=(.+?)$",response.url)[0]
            
            if response.xpath("//h1[1]/text()").extract()[-1].split():
                item['companyname'] = ''.join(response.xpath("//h1[1]/text()").extract()[-1])
            else:
                item['companyname'] = ''.join(response.xpath("//h1[1]/text()").extract()[0])
            print()
            item['tel'] = ''.join(re.findall(r"@phone=(.+?)@",''.join(response.xpath("//a[contains(@class,'displayphonenumber')]/@gjalog").extract())))
            item['address'] = ''.join(response.xpath("//span[contains(text(),'上课地址：')]/following-sibling::p[1]//text()").extract())
            item['fuwutese'] = ''
            item['tigongfuwu'] = ''
            item['fuwufanwei'] = ''
            item['lianxiren'] = ''.join(response.xpath("//span[contains(text(),'联系人：')]/following-sibling::p/text()").extract())
            item['shangjiadizhi'] = ''
            item['yingyeshijian'] = ''.join(response.xpath("//span[contains(text(),'开课时间')]/following-sibling::p/text()").extract())
            item['website'] = ''
            item['jianjie'] = ''.join(response.xpath("//h3[text()='详细信息']/following-sibling::div[1]").extract())
            item['ID'] = companyid
            item['table'] = self.name
            # print(item)
            for key in item:
                if item[key].strip() == '':
                    item[key] = '无'
                else:
                    item[key] = item[key].strip() 
            yield item
                # pass
            self.push_url(companyid,3)
        #职业培训
        elif (response.status==200 or response.status==304 )and ('redirect_urls' not in response.meta) and(response.xpath("//div[@id='wrapper']//div[@class='leftbox clearfix']")) :
            # spans = response.xpath("//article[@class='main']/preceding-sibling::article[1]")  #顶部三个主要信息
            item = qianzhan_detail()
            companyid = re.findall(r"companyid=(.+?)$",response.url)[0]
            
            if response.xpath("//h1[1]/text()").extract()[-1].split():
                item['companyname'] = ''.join(response.xpath("//h1[1]/text()").extract()[-1])
            else:
                item['companyname'] = ''.join(response.xpath("//h1[1]/text()").extract()[0])
            print()
            item['tel'] = ''.join(re.findall(r"@phone=(.+?)@",''.join(response.xpath("//a[contains(@class,'displayphonenumber')]/@gjalog").extract())))
            item['address'] = ''.join(response.xpath("//span[contains(text(),'开课校区')]/parent::li/text()").extract())
            item['fuwutese'] = ''.join(response.xpath("//span[contains(text(),'参考学费：')]/following-sibling::b/text()").extract())
            item['tigongfuwu'] = ';'.join(response.xpath("//span[contains(text(),'上课班型')]/parent::li/text()").extract())
            item['fuwufanwei'] = ';'.join(response.xpath("//span[contains(text(),'服务范围')]/following-sibling::p/a/text()").extract())
            item['lianxiren'] = ''.join(response.xpath("//i[contains(text(),'联系人')]/parent::span/text()").extract())
            item['shangjiadizhi'] = ''.join(response.xpath("//span[contains(text(),'商家地址')]/following-sibling::p//text()").extract())
            item['yingyeshijian'] = ''.join(response.xpath("//span[contains(text(),'上课时间')]/parent::li[1]/text()").extract())
            item['website'] = ''.join(response.xpath("//span[contains(text(),'网  址：')]/following-sibling::p/a/text()").extract())
            item['jianjie'] = ''.join(response.xpath("//span[contains(text(),'课程简介')]/parent::div[1]/following-sibling::div[1]").extract())
            item['ID'] = companyid
            item['table'] = self.name
            # print(item)
            for key in item:
                if item[key].strip() == '':
                    item[key] = '无'
                else:
                    item[key] = item[key].strip() 
            yield item
                # pass
            self.push_url(companyid,3)
        else: #设置失败，并pushurl
            if("jump.zhineng" in response.url):
                companyid = re.findall(r"companyid=(.+?)$",response.url)[0]
                self.push_url(companyid,2)
            elif("redirect_urls" in response.meta):
                companyid = re.findall(r"companyid=(.+?)$",response.meta['redirect_urls'][0])[0]
                self.push_url(companyid,2)
            elif 'confirm' not in response.url: #如果不是验证码，则设置采集失败
                companyid = re.findall(r"companyid=(.+?)$",response.url)[0]
                self.push_url(companyid,2)
            # elif response.status == 403:
            #     self.push_url(response.url,404) #重新采集
            # elif response.status == 302 :
            # #获取跳转前的地址，并修改数据库地址
            #     print(response.headers['Location'])
            #     originurl = re.findall('^(.+?)\?item',response.url)[0]
            #     refferurl = re.findall('^(.+?)\?item',bytes.decode(response.headers['Location']))[0]
            #     Sql.exe('update '+self.name+' set url=%s where url=%s',(refferurl,originurl))
            #     self.push_url(refferurl,404)
            # else:
            #     prev_url = response.meta['redirect_urls'][0]
            #     self.push_url(prev_url,404)
        