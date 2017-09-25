# -*- coding: utf-8 -*-
from .sql import Sql
from ganji.items import qianzhan_detail
from ganji.items import qianzhan_list
from ganji.items import ganji_cate
from ganji.items import xc_linedetail
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class XuexiPipeline(object):
#     def process_item(self, item, spider):
#         if isinstance(item, XuexiItem):
#             name_id = item['name_id']
#             ret = Sql.select_name(name_id)
#             if ret[0] == 1:
#                 print('已经存在了')
#                 pass
#             else:
#                 xs_name = item['name']
#                 xs_author = item['author']
#                 category = item['category']
#                 Sql.insert_dd_name(xs_name, xs_author, category, name_id)
#                 print('开始存小说标题')
class GanjicatePipeline(object):   #批量插入list
    def process_item(self, item, spider):
        if isinstance(item, ganji_cate):
            
            tem = []
            for i in range(0,len(item['url'])):
                tem.append(item['name'][i])
                tem.append(item['url'][i])
                tem.append(item['parent'][i])
                tem.append(item['level'][i])
            parms = tuple(tem)
            print(parms)
            sqls = "insert ignore ganji_yell_cate  (name,url,parent,level) values "
            for num in range(0,len(item['url'])) :
                sqls += ' (%s,%s,%s,%s),'
            Sql.exe(sqls[0:-1],parms)
            print('存库完成！')
class XingtaipagePipeline(object):   #批量插入list
    def process_item(self, item, spider):
        if isinstance(item, qianzhan_list):
            print('开始存库！')
            parms = tuple(item['url'])
            sqls = "insert ignore xc_linedetail_hebei  (url) values "
            for num in range(1,len(item['url'])+1) :
                sqls += ' (%s),'
            Sql.exe(sqls[0:-1],parms)
            print('存库完成！')
class XingtaifenyePipeline(object):   #批量插入list
    def process_item(self, item, spider):
        if isinstance(item, qianzhan_list):
            parms = tuple(item['url'])
            sqls = "insert qianzhan_xingtai_allpage  (url) values "
            for num in range(1,len(item['url'])+1) :
                sqls += ' (%s),'
            Sql.exe(sqls[0:-1],parms)
            print('存库完成！')
class XingtaidetailPipeline(object):   #批量插入list
    def process_item(self, item, spider):
        if isinstance(item, xc_linedetail):
            parms =  tuple(item.values())
            del(item['ID']) #去掉不需要的key
            sets = ''
            for key in item:
                sets += key+'=%s,'
            Sql.exe("update xc_linedetail_hebei  set "+sets+"complete=1  where id=%s ",parms)
            print('存库完成！')

