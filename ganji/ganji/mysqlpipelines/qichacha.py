# -*- coding: utf-8 -*-
from .sql import Sql
from ganji.items import qichacha_detail
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class QichachaPipeline(object):   #批量插入list
    def process_item(self, item, spider):
        if isinstance(item, qichacha_detail):
            temp_id = item['ID']
            del(item['ID']) #去掉不需要的key
            parms =  tuple(item.values())
            sets = ''
            for key in item:
                sets += key+'=%s,'
            # print("update qichacha  set "+sets+"httpcode=200  where id="+str(temp_id)+" ")
            # print(parms)
            Sql.exe("update qichacha  set "+sets+"httpcode=200,success=1  where id="+str(temp_id)+" ",parms)
            print('存库完成！')