#! -*- encoding:utf-8 -*-
import base64

# 代理服务器
# proxyServer = "http://proxy.abuyun.com:9010"
proxyServer = "http://proxy.abuyun.com:9020" #动态版

# 代理隧道验证信息
proxy_user_pass = 'XXXXXXXXXXXX:XXXXXXXXXXXXXX' #动态版，自行填写
proxyAuth = "Basic " + base64.b64encode(proxy_user_pass.encode('utf-8')).decode()

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth
        # request.headers["Proxy-Switch-Ip"] = 'yes'
        # request.cookies = cookies


