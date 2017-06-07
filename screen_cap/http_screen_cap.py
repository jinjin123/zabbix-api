#!/usr/bin/env python
# -*- coding: utf-8 -*-
# task argument to get the  mapping grapth 
#hostid  and graphid  its need  , 每个host的id都不一样 ，从hostid 往下级拿graphid    hostid=xx&graphid=xx&
import json, traceback
import datetime
import cookielib, urllib2,urllib
import time

class ZabbixGraph():
    def __init__(self,url="http://172.16.102.128:81/index.php",name="admin",password="zabbix"):
        self.url=url
        self.name=name
        self.passwd=password
        #初始化的时候生成cookies
        cookiejar = cookielib.CookieJar()
        urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        values = {"name":self.name,'password':self.passwd,'autologin':1,"enter":'Sign in'}
        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        try:
            urlOpener.open(request,timeout=10)
            self.urlOpener=urlOpener
        except urllib2.HTTPError, e:
            print e
    def GetGraph(self,url="http://172.16.102.128:81/chart2.php",values={'width': 800, 'height': 200, 'hostid': '', 'graphid': '', 'stime': time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())), 'period': 3600},image_dir="/home/azureuser"):
        data=urllib.urlencode(values)
        request = urllib2.Request(url,data)
        url = self.urlOpener.open(request)
        image = url.read()
        imagename="%s/%s_%s_%s.jpg" % (image_dir, values["hostid"], values["graphid"], values["stime"])
        #imagename="%s/%s_%s.jpg" % (image_dir, values["graphid"], values["stime"])
        f=open(imagename,'wb')
        f.write(image)
        return '1'

if __name__ == "__main__":
    #hostid = ['10107','10108','10109','10110','10111','10112']
    hostid = ['10107','10108']
    #graphidm = ['594','566','566','594','601','608']
    graphidm = ['594','566']
    graphidd = ['624','643']
    #graphidd = ['624','643','','','','','']
    graph = ZabbixGraph()
    stime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    values = {'width': 800, 'height': 200, 'hostid': '10107', 'graphid': '594', 'stime': stime, 'period': 300}
    graph.GetGraph("http://172.16.102.128:81/chart2.php",values,"/root/screen")
    #for h in  hostid:
    #	for m in graphidm:
	#	values = {'width': 800, 'height': 200, 'hostid': h, 'graphid': m, 'stime': stime, 'period': 300}
 	#	graph.GetGraph("http://172.16.102.128:81/chart2.php",values,"/root/screen")
	#for d in graphidd:
    	#	values = {'width': 800, 'height': 200, 'hostid': h, 'graphid': d, 'stime': stime, 'period': 300}
    	#	graph.GetGraph("http://172.16.102.128:81/chart2.php",values,"/root/screen")
