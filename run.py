#coding=utf-8
#Author : TimoQAQ
#Author's QQ : 2190778650
#Version ：2.0
#Date : 2018-9-3
#需要安装的第三方库:requests BeautifulSoup selenium+火狐驱动

import re
import time
import base64
import requests
from http import cookiejar
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

Copyright = ''
speed = 0.2 #刷课时间间隔，默认200毫秒
path = 'http://study.zhihuishu.com'
entrance = 'https://passport.zhihuishu.com/login?service=http://online.zhihuishu.com/onlineSchool/'

def convert():#切换到当前页面
	time.sleep(3)
	windows = browser.window_handles
	browser.switch_to.window(windows[-1])

def load():#加载网页，获取cookies和页面
	input('请自行输入账号密码 并打开要刷课的视频页面 然后按回车开始刷课...')
	convert()
	
	#保存cookies到requests.session
	cookie = ["'" + item["name"] + "':'" + item["value"] + "'" for item in browser.get_cookies()]
	cookiestr = ','.join(item for item in cookie)
	cookiestr = '{' + cookiestr + '}'
	session.cookies = requests.utils.cookiejar_from_dict(eval(cookiestr), cookiejar=None, overwrite=True)
	
	#由于不知道怎么将selenium的cookies格式转换为带域名的ccookiejar,所以为csrftoken、SERVERID添加域名
	token = session.cookies['csrftoken']
	serverid = session.cookies['SERVERID']
	session.cookies.set('csrftoken', None)
	session.cookies.set('SERVERID', None)
	session.cookies.set('csrftoken', token, path='/', domain=path[7:])
	session.cookies.set('SERVERID', serverid, path='/', domain=path[7:])
	
	print('成功获取cookie...')
	print('返回页面...')
	return (browser.page_source)

def studiedId(params):#传入一个标准参数字典,返回studiedId
	t = int(time.time() * 1000) #毫秒级时间戳
	url = path + '/json/learning/prelearningNote?time=' + str(t)

	header = {
	'Host': path[7:],
	'Connection': 'keep-alive',
	'Accept': '*/*',
	'Origin': path,
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': path + '/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
	}
	
	data = {
	'rid':params['rid'],
	'studentCount':params['studentCount'],
	'lessonId':params['lessonId'],
	'PCourseId':params['PCourseId'],
	'chapterId':params['_chapterid'],
	'lessonVideoId':'',
	'userId':params['userId'],
	'videoId':params['videoId'],
	'studyStatus':''
	}
	
	response = session.post(url, headers = header, data = data) #POST数据包
	studie_Id = re.search(r'"id":([0-9]*),"is',response.text).group(1)  #匹配response里的studiedId

	return(studie_Id)

def saveCache(params):#存入缓存
	t = int(time.time() * 1000) #毫秒级时间戳
	url = path + '/json/learning/saveCacheIntervalTime?time=' + str(t)
		
	header = {
	'Host': path[7:],
	'Connection': 'keep-alive',
	'Accept': '*/*',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': path + '/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
	}
	
	data = {
	'__learning_token__':base64.b64encode(studiedId(params).encode('utf-8')), #加密studiedId生成__learning_token__
	'ev':encode([params['rid'], params['_chapterid'], params['courseId'], params['lessonId'], studyTime(params['_videosize']), studyTime(params['_videosize']), params['videoId'], '0']),
	'csrfToken':session.cookies['csrftoken']
	}

	response = session.post(url, headers = header, data = data) #发送数据包
	print('saveCache:\t' + params['_name'] + '\t', response.status_code)

def saveDatabase(params):#存入数据库
	t = int(round(time.time() * 1000)) #毫秒级时间戳
	url = path + '/json/learning/saveDatabaseIntervalTime?time=' + str(t)
	
	header = {
	'Host': path[7:],
	'Connection': 'keep-alive',
	'Accept': '*/*',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': path + '/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
	}
	
	data = {
	'__learning_token__':base64.b64encode(studiedId(params).encode('utf-8')), #加密studiedId生成__learning_token__
	'ev':encode([params['rid'], params['lessonId'], '0', params['videoId'], '1', params['studyStatus'], studyTime(params['_videosize']), studyTime(params['_videosize']), params['_videosize']]),
	'csrfToken':session.cookies['csrftoken']
	}
	
	response = session.post(url, headers = header, data = data) #发送数据包
	print('saveDatabase:\t' + params['_name'] + '\t', response.status_code)

def studyTime(videosize):#输入视频长度,返回秒级时间戳
	hms = videosize.split(':') #00:00:00 分割 时:分:秒
	hms_in_s = int(hms[0])*3600+int(hms[1])*60+int(hms[2]) #计算秒数
	return(str(hms_in_s))

def html_input(page):#传入一个html页面,返回一个input_hidden字典
	container = {}
	soup = BeautifulSoup(page, 'html.parser')
	input = soup.find_all('input',attrs={'type':'hidden'}) #BeautifulSoup匹配所有type为hidden的<input>标签
	#生成隐域常量字典
	for each in input:
		container[each.get('id')] = each.get('value')

	return(container)

def html_li(page):#传入一个html页面,返回一个视频参数的二维字典{videoId:{},videoId:{}}
	container = {}
	soup = BeautifulSoup(page, 'html.parser')
	li = soup.find_all('li',id=re.compile('video-[0-9]+')) #BeautifulSoup匹配对应视频的<li>标签
	#生成含有每个视频信息的二维字典
	for each in li:
		container[each.get('_videoid')] = {'_videoid':each.get('_videoid'), '_name':each.get('_name'), 'watchstate':each.get('watchstate'), '_chapterid':each.get('_chapterid'), 'lessonId':each.get('_lessonid'), '_videosize':each.get('_videosize')}

	return(container)

def encode(param):#由JS翻译过来的加密函数,返回ev参数
	a = ''
	ev = ''
	for c in range(len(param)):
		a += param[c]+';'
	a=a[:len(a)-1]
	for c in range(len(a)):
		d = ord(a[c])^ord(Copyright[c % len(Copyright)])
		e = hex(d)[2:]
		if len(e) < 2 :e ='0'+e
		e = e[len(e)-4:]
		ev += e
	return(ev)

def main(page,rate):#主函数
	input = html_input(page) #获取隐域的常量
	li = html_li(page) #获取<li>标签里的视频参数
	global Copyright
	Copyright = input['copyright']
	num = int(len(li)*rate/100) #将进度转化为要刷的视频数量
	print('开始刷课...')
	
	for each in li.values(): #用for循环遍历每一个视频
		
		#刷到相应的视频数量时跳出循环
		if num == 0:break
		num -= 1
		
		if each['watchstate'] != '1': #判断改视频观看状态，若不等于1(未观看or没看完)，则进行刷课
			temp = input
			temp.update(each) #更新字典，将视频参数字典更新到常量字典里面
			
			#调用函数发包
			saveCache(temp)
			saveDatabase(temp)
			time.sleep(speed) #刷课时间间隔
		
	print('刷课结束!')

if __name__ == '__main__':#入口函数
	options = Options()
	options.add_argument('--disable-gpu')
	browser = webdriver.Firefox(firefox_options=options)
	session = requests.Session() #建立会话
	browser.get(entrance) #打开登录页面

	while True:
		try:
			rate = int(input('请输入刷课进度(0-100):')) #输入要刷到的进度，默认50%
		except:
			rate = 50
		if 0 < rate <= 100:
			break
		print('输入有误,请重新输入!')
	
	html = load() #调用load()获取cookie和html页面
	main(html,rate) #传入页面和进度，进入执行函数
