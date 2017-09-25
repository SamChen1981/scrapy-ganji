# -*- coding: utf-8 -*-
from ganji.mysqlpipelines.sql import Sql
# 建表语句

qichacha = """
create table if not exists `%s` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) DEFAULT NULL COMMENT '公司名称',
    `tel` varchar(255) DEFAULT NULL COMMENT '电话',
    `website` varchar(255) DEFAULT NULL COMMENT '网站',
    `address` varchar(255) DEFAULT NULL COMMENT '地址',
    `faren` varchar(255) DEFAULT NULL COMMENT '法人代表',
    `zhuceziben` varchar(255) DEFAULT NULL,
    `zhuceshijian` varchar(255) DEFAULT NULL,
    `status` varchar(255) DEFAULT NULL COMMENT '状态',
    `gszch` varchar(255) DEFAULT NULL COMMENT '工商注册号',
    `zuzhicode` varchar(255) DEFAULT NULL COMMENT '组织机构代码',
    `xinyongcode` varchar(255) DEFAULT NULL COMMENT '信用代码',
    `category` varchar(255) DEFAULT NULL COMMENT '企业类型',
    `hangye` varchar(255) DEFAULT NULL,
    `yingye` varchar(255) DEFAULT NULL COMMENT '营业期限',
    `hezhun` varchar(255) DEFAULT NULL COMMENT '核准日期',
    `dengji` varchar(255) DEFAULT NULL COMMENT '登记机关',
    `regaddress` varchar(255) DEFAULT NULL COMMENT '注册地址',
    `jingying` varchar(255) DEFAULT NULL COMMENT '经营范围',
    `url` varchar(255) DEFAULT NULL,
    `success` tinyint(1) DEFAULT '0' COMMENT '采集成功 0未采集，1采集成功，2采集失败',
    `httpcode` char(3) DEFAULT NULL COMMENT 'http状态码',
    `email` varchar(255) DEFAULT NULL COMMENT '邮箱',
    PRIMARY KEY (`id`),
    UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""
ganji_detail = """
create table if not exists `ganji_%s_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) DEFAULT NULL COMMENT '地址',
  `address` varchar(255) DEFAULT NULL,
  `fuwufanwei` varchar(255) DEFAULT NULL COMMENT '服务范围',
  `fuwutese` varchar(255) DEFAULT NULL COMMENT '服务特色',
  `jianjie` text COMMENT '简介',
  `lianxiren` varchar(255) DEFAULT NULL COMMENT '联系人',
  `companyname` varchar(255) DEFAULT NULL COMMENT '公司名称',
  `shangjiadizhi` varchar(255) DEFAULT NULL COMMENT '商家地址',
  `tel` varchar(255) DEFAULT NULL,
  `tigongfuwu` varchar(255) DEFAULT NULL COMMENT '提供服务',
  `website` varchar(255) DEFAULT NULL COMMENT '网站',
  `yingyeshijian` varchar(255) DEFAULT NULL COMMENT '营业时间',
  `cate` varchar(255) DEFAULT NULL COMMENT '分类',
  `success` tinyint(1) DEFAULT '0' COMMENT '采集成功',
  `publish` tinyint(1) DEFAULT '0' COMMENT '发布成功',
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `success` (`success`) USING HASH
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;
"""

class  Ganji:
    @classmethod
    def check(cls, city_name):
        #check the table is exist
        res = Sql.res('show tables',(),'all')
        table_name = ('ganji_'+city_name+'_detail',)
        if table_name in res:
            pass
        else:
            Sql.exe(ganji_detail,()) #create table
        #insert cityurls
        count = Sql.res('select count(*) from ganji_all_cityurl WHERE url LIKE "http://'+city_name+'.%"',())
        if count[0] != 0 :
            #insert urls
            citys = Sql.res('select url,city from ganji_city_squre where city="%s"',(city_name,),'all')
            print(citys)