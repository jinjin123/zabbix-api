#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import sys
import json
import time
from PIL import Image
from conf.INIFILES import read_config, write_config
from selenium import webdriver
import os
import datetime
from conf.BLog import Log
from get_pic import getpic
import re
from lxml import etree
reload(sys)
sys.setdefaultencoding('utf-8')


#####tar -jxvf phantomjs-2.1.1-linux-x86_64.tar.bz2
######mv phantomjs-2.1.1-linux-x86_64 /usr/local/phantomjs-2.1.1


class WeiXin(object):
    def __init__(self, corpid, corpsecret): # 初始化的时候需要获取corpid和corpsecret，需要从管理后台获取
        self.__params = {
            'corpid': corpid,
            'corpsecret': corpsecret
        }

        self.url_get_token = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        self.url_send = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        self.url_uploadimg = 'https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg'
        self.img_url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload'

        self.__token = self.__get_token()
        self.__token_params = {
            'access_token': self.__token
        }

    def __raise_error(self, res):
        raise Exception('error code: %s,error message: %s' % (res.json()['errcode'], res.json()['errmsg']))
        global senderr
        global sendstatus
        sendstatus = False
        senderr = 'error code: %s,error message: %s' % (res.json()['errcode'], res.json()['errmsg'])

    def __get_token(self):
        # print self.url_get_token
        headers = {'content-type': 'application/json'}
        res = requests.get(self.url_get_token, headers=headers,  params=self.__params)

        try:
            return res.json()['access_token']
        except:
            self.__raise_error(res.content)


    def send_message(self,  agentid, messages, userid, toparty,totag):
        payload = {
            'touser': userid,
            'toparty': toparty,
            'totag': totag,
            'agentid': agentid,
            "msgtype": "news",
            "news": messages
        }
        headers = {'content-type': 'application/json'}
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        params = self.__token_params
        res = requests.post(self.url_send, headers=headers, params=params, data=data,verify=False)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def get_media_ID(self, path):
        params = self.__token_params
        params['type'] = 'image\r\n'
        data = {'media': open(path, 'rb')}
        r = requests.post(url=self.img_url, params=params, files=data,verify=False)
        dict = r.json()
   	logwrite(True, dict)
        return dict['media_id']

    def get_imaging(self, path):
        params = self.__token_params
        data = {'media': open(path, 'rb')}
        r = requests.post(url=self.url_uploadimg, params=params, files=data,verify=False)
        dict = r.json()
   	logwrite(True, dict)
        return dict['url']


def main(send_to, subject, content):
    try:
        global sendstatus
        global senderr
        data = ''
        messages = {}
        body = {}
        config_file_path = get_path()
        CorpID = read_config(config_file_path, 'wei', "CorpID")
        CorpSecret = read_config(config_file_path, 'wei', "CorpSecret")
        agentid = read_config(config_file_path, 'wei', "agentid")
        web = read_config(config_file_path, 'wei', "web")
        # content = json.loads(content)
        messages["message_url"] = web
        root = etree.fromstring(content)
        itemid = root.xpath(u"监控ID")[0].text
        itemvalue = root.xpath(u"监控取值")[0].text
        s = re.match(r'^[0-9\.]+(\s\w{0,3})?$', itemvalue)
        # s = re.match(r'^[0-9\.]+$', itemvalue.split(' ')[0])
        #if s:
        #    body["url"] = web + "history.php?action=showgraph&itemids[]=" + itemid
        #else:
            #body["url"] = web + "history.php?action=showvalues&itemids[]=" + itemid
        #    body["url"] = web + "history.php?action=showgraph&itemids[]=" + itemid
        warn_message = ''
        if root.xpath(u"当前状态")[0].text == 'PROBLEM':
            body["title"] = "服务器故障"
            warn_message += subject + '\n'
            warn_message += '详情：\n'
            warn_message += '告警等级：' + root.xpath(u"告警等级")[0].text + '\n'
            warn_message += '告警时间：' + root.xpath(u"告警时间")[0].text + '\n'
            warn_message += '告警地址：' + root.xpath(u"告警地址")[0].text + '\n'
            warn_message += '持续时间：' + root.xpath(u"持续时间")[0].text + '\n'
            warn_message += '监控项目：' + root.xpath(u"监控项目")[0].text + '\n'
            warn_message += root.xpath(u"告警主机")[0].text + '故障(' + root.xpath(u"事件ID")[0].text+ ')'
        else:
            body["title"] = "服务器恢复"
            warn_message += subject + '\n'
            warn_message += '详情：\n'
            warn_message += '告警等级：' +  root.xpath(u"告警等级")[0].text + '\n'
            warn_message += '恢复时间：' +  root.xpath(u"恢复时间")[0].text + '\n'
            warn_message += '告警地址：' +  root.xpath(u"告警地址")[0].text + '\n'
            warn_message += '持续时间：' +  root.xpath(u"持续时间")[0].text + '\n'
            warn_message += '监控项目：' +  root.xpath(u"监控项目")[0].text + '\n'
            warn_message += root.xpath(u"告警主机")[0].text + '恢复(' +  root.xpath(u"事件ID")[0].text+ ')'
        body["title"] = "服务器故障"
        body['description'] = warn_message
        wx = WeiXin(CorpID, CorpSecret)
        pic_path = getpic(itemid, s)
        picurl = wx.get_imaging(pic_path)
   	logwrite(True, picurl)
        #body['url'] = 'http://shp.qpic.cn/bizmp/ExibXibqPoLic7cWGI5pS8IumjRWW2bbBFTrasic2QzzTB5TuYKjoGHWIQ/'
	body['url'] = picurl
        #body['picurl'] = 'http://shp.qpic.cn/bizmp/ExibXibqPoLic7cWGI5pS8IumjRWW2bbBFTrasic2QzzTB5TuYKjoGHWIQ/'
	body['picurl'] = picurl
        data = []
        data.append(body)
        messages['articles'] = data
        data = wx.send_message(userid=send_to, agentid=agentid, messages=messages,toparty=4,totag=4)
        sendstatus = True
    except Exception, e:
        senderr = str(e)
        sendstatus = False
    logwrite(sendstatus, data)


def get_path():
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_path = path + '/config.ini'
    return config_path


def logwrite(sendstatus, content):
    logpath = '/var/log/zabbix/weixin'
    if not sendstatus:
        content = senderr
    t = datetime.datetime.now()
    daytime = t.strftime('%Y-%m-%d')
    daylogfile = logpath+'/'+str(daytime)+'.log'
    logger = Log(daylogfile, level="info", is_console=False, mbs=5, count=5)
    os.system('chown zabbix.zabbix {0}'.format(daylogfile))
    logger.info(content)


def get_item_pic(url, user, passwd, itemid, flag):
    try:
        driver = webdriver.PhantomJS("/usr/local/phantomjs-2.1.1/bin/phantomjs",service_log_path=os.path.devnull)
        # driver = webdriver.PhantomJS(executable_path='/usr/local/phantomjs-2.1.1/bin/phantomjs', service_log_path='/var/log/ghostdriver.log', service_args=["--webdriver-loglevel=NONE"])
        driver.get(url)
        driver.set_window_size(640, 480)
        picpath = "/usr/local/zabbix/scripts/pic"
        driver.find_element_by_id("name").send_keys(user)     #输入用户名
        driver.find_element_by_id("password").send_keys(passwd)     #输入用户名
        driver.find_element_by_id("enter").click()
        if flag:
            item_url = url + "history.php?action=showgraph&fullscreen=1&period=30&itemids[]=" + itemid
        else:
            #item_url = url + "history.php?action=showvalues&fullscreen=1&period=30&itemids[]=" + itemid
            item_url = url + "history.php?action=showgraph&fullscreen=1&period=30&itemids[]=" + itemid
        driver.get(item_url)
        temp_name = picpath+"/"+itemid + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
        time.sleep(0.5)
        driver.save_screenshot(temp_name)
        driver.close()
        driver.quit()
        # shutil.move(temp_name, backpath)
        if not flag:
            im = Image.open(temp_name)
            im = im.crop((0, 0, 640, 480))
            im.save(temp_name)
        return temp_name
    except Exception, e:
        senderr = str(e)
        sendstatus = False
    logwrite(sendstatus, e)


def getpic(item_id, s):
    try:
        config_file_path = get_path()
        user = read_config(config_file_path, 'zabbix', "user")
        passwd = read_config(config_file_path, 'zabbix', "passwd")
        url = read_config(config_file_path, 'wei', "web")
        ppath = get_item_pic(url, user=user, passwd=passwd, itemid=item_id, flag=s)
        global sendstatus
        sendstatus = True
   	logwrite(sendstatus, ppath)
        return ppath
    except Exception, e:
        global senderr
        senderr = str(e)
        global sendstatus
        sendstatus = False
    logwrite(sendstatus, e)

def geti():
	path = '/usr/local/zabbix/scripts/pic/23706_20170626000058.png'
        params = {'access_token': '2F_Pcr2TeL4Q4eqgTjZxuDLTm1ndVVaBYhOPI5uLFrj8jd6gbBifGUhKRYGQKscU'}
        data = {'media': open(path, 'rb')}
        r = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg', params=params, files=data)
        dict = r.json()
	print dict

def getid():
	path = '/usr/local/zabbix/scripts/pic/23706_20170626000058.png'
        params = {'access_token': '2F_Pcr2TeL4Q4eqgTjZxuDLTm1ndVVaBYhOPI5uLFrj8jd6gbBifGUhKRYGQKscU'}
        params['type'] = 'image\r\n'
        data = {'media': open(path, 'rb')}
        r = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/media/upload', params=params, files=data)
        dict = r.json()
	print dict

def send_msg(to_user="13113252872",to_party="",to_tag="",application_id=4,safe=0):
    try:
        data = {
                 "touser": to_user,
                 "toparty": to_party,
                 "totag": to_tag,
                 "msgtype": "news",
                 "agentid": application_id,
                 "news": {
                        "articles":[
                                {
                                          "title": "health",
                                        "description": "告警主机45.76.13.251告警主机\fsdfasfdasfasfdasfsafasfsafsaf\nfdsfasfdasfdasfasfas\nfdsafsafsafasfasfasfsadfsafsa\nfdsafdsafsafasfaf\nfdsfdsafdsafdasf\nf",
					"url": "http://shp.qpic.cn/bizmp/ExibXibqPoLic7cWGI5pS8IumjRWW2bbBFTrasic2QzzTB5TuYKjoGHWIQ/",
					"picurl": "http://shp.qpic.cn/bizmp/ExibXibqPoLic7cWGI5pS8IumjRWW2bbBFTrasic2QzzTB5TuYKjoGHWIQ/"
                                },
                        ]
                    }
                 }
        data = json.dumps(data,ensure_ascii=False)
        token = 'sTzKi0dufmCAnaJhjbMQMmdNWPaQjfhBHuvdEE4YdM-Q3c4oFaVTCUxHHJAEaUpm'
        req = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}'.format(token),data,verify=False)
        print req.json()
    except Exception,e:
        print str(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_to = sys.argv[1]
        subject = sys.argv[2]
        content = sys.argv[3]
        logwrite(True, send_to)
        logwrite(True, subject)
        logwrite(True, content)
        main(send_to, subject, content)
	#send_msg()
"""
	wx =  WeiXin('wxfcf60e7eba5f47f3', 'OhsSU18oK_W3IGT-z_LcvCu379d1_cO6OFyNhciCzX1FyeJKJNLN3yHolsfCmWAJ')
	picurl= "http://shp.qpic.cn/bizmp/ExibXibqPoLic7cWGI5pS8IumjRWW2bbBFTrasic2QzzTB5TuYKjoGHWIQ/"
	messages = {}
	body = {}
	body["title"] = "服务器故障"
	body['description'] = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
	body['picurl'] = picurl
	data = []
	data.append(body)
	messages['articles'] = data
	data = wx.send_message(userid=13113252872, agentid=4,messages=messages,toparty=4,totag=4)
	print data
"""
