#coding=utf-8
#Version ：2.2
#Date : 2018-9-5
#Author : TimoQAQ
#Author's QQ : 2190778650
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

speed = 0.2 #刷课时间间隔，默认200毫秒
path = 'http://study.zhihuishu.com'
entrance = 'https://passport.zhihuishu.com/login?service=http://online.zhihuishu.com/onlineSchool/'

def convert():#切换到当前页面
	time.sleep(2)
	windows = browser.window_handles
	browser.switch_to.window(windows[-1])
	return(0)

def load():#加载网页，获取cookies和页面
	input('打开该门课程的视频页面,待页面加载完成后按回车键开始刷课...')
	convert()
	#保存浏览器cookies到requests.session
	cookie = ["'" + item["name"] + "':'" + item["value"] + "'" for item in browser.get_cookies()]
	cookiestr = ','.join(item for item in cookie)
	cookiestr = '{' + cookiestr + '}'
	session.cookies = requests.utils.cookiejar_from_dict(eval(cookiestr), cookiejar=None, overwrite=True)
	#由于不知道怎么将selenium的cookies格式转换为带域名的ccookiejar,所以为不含域名的csrftoken、SERVERID添加域名
	try:
		token = session.cookies['csrftoken']
		serverid = session.cookies['SERVERID']
		print('成功获取cookie...')
	except:
		print('没有获取到cookie,可能是视频页面没有加载完成,请重新尝试!')
		return(1)
	#新建两个cookie对象,并保存值和域名
	session.cookies.set('csrftoken', None)
	session.cookies.set('SERVERID', None)
	session.cookies.set('csrftoken', token, path='/', domain=path[7:])
	session.cookies.set('SERVERID', serverid, path='/', domain=path[7:])
	#判断返回页面
	if browser.page_source != None:
		print('返回页面...')
	else:
		print('没有获取到页面,请重新尝试!')
		return(1)
	return (browser.page_source)

def studiedId(params):#传入一个标准参数字典,返回studiedId
	count = 0
	t = int(time.time() * 1000) #毫秒级时间戳
	url = path + '/json/learning/prelearningNote?time=' + str(t)

	header = {
	'Host': path[7:],
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
	'Accept': '*/*',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': path + '/learning/videoList;jsessionid=' + session.cookies['JSESSIONID'] + '?FCcourseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'X-Requested-With': 'XMLHttpRequest',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0'
	}
	
	data = {
	'rid':params['rid'],
	'studentCount':params['studentCount'],
	'lessonId':params['_lessonId'],
	'PCourseId':params['PCourseId'],
	'chapterId':params['_chapterid'],
	'lessonVideoId':'',
	'userId':params['userId'],
	'videoId':params['_videoid'],
	'studyStatus':''
	}

	if params['_lessonvideoid'] != '0':
		data['lessonVideoId'] = params['_lessonvideoid']

	while True:
		try:
			response = session.post(url, headers = header, data = data) #POST数据包
			studie_Id = re.search(r'"id":([0-9]*),"is',response.text).group(1)  #匹配response里的studiedId
			break
		except:
			if count == 5:
				input('无法获取studiedId,请按回车键重新尝试!')
				return(1)
			count += 1
			print('没有获取到studiedId,正在尝试重新获取...')
	return(studie_Id)

def saveCache(params,studie_Id):#存入缓存
	t = int(time.time() * 1000) #毫秒级时间戳
	url = path + '/json/learning/saveCacheIntervalTime?time=' + str(t)
		
	header = {
	'Host': path[7:],
	'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
	'Accept': '*/*',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': path + '/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'X-Requested-With': 'XMLHttpRequest',
	'Connection': 'keep-alive'
	}
	
	data = {
	'__learning_token__':base64.b64encode(studie_Id.encode('utf-8')), #加密studiedId生成__learning_token__
	'ev':encode([params['rid'], params['_chapterid'], params['courseId'], params['_lessonId'], params['_videosize'], studyTime(params['_videosize']), params['_videoid'], params['_lessonvideoid']]),
	'csrfToken':session.cookies['csrftoken']
	}

	if params['_lessonvideoid'] != '0':
		data['lessonVideoId'] = params['_lessonvideoid']

	response = session.post(url, headers = header, data = data) #发送数据包
	return(response.status_code)

def saveDatabase(params,studie_Id):#存入数据库
	t = int(round(time.time() * 1000)) #毫秒级时间戳
	url = path + '/json/learning/saveDatabaseIntervalTime?time=' + str(t)
	
	header = {
	'Host': path[7:],
	'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
	'Accept': '*/*',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': path + '/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'X-Requested-With': 'XMLHttpRequest',
	'Connection': 'keep-alive'
	}

	data = {
	'__learning_token__':base64.b64encode(studie_Id.encode('utf-8')), #加密studiedId生成__learning_token__
	'ev':encode([params['rid'], params['_lessonId'], params['_lessonvideoid'], params['_videoid'], '1', params['studyStatus'], studyTime(params['_videosize']), studyTime(params['_videosize']), params['_videosize']]),
	'csrfToken':session.cookies['csrftoken']
	}
	
	response = session.post(url, headers = header, data = data) #发送数据包
	return(response.status_code)

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
	li = soup.find_all('li',id=re.compile('video-[0-9]{2,10}')) #BeautifulSoup匹配对应视频的<li>标签
	#生成含有每个视频信息的二维字典
	for each in li:
		videosize = each.find('span', attrs={'class':'time fl'}).text
		container[each.get('_videoid')] = {'_videoid':each.get('_videoid'), '_name':each.get('_name'), 'watchstate':each.get('watchstate'), '_chapterid':each.get('_chapterid'), '_lessonId':each.get('_lessonid'), '_videosize':videosize, '_lessonvideoid':each.get('_lessonvideoid')}
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
	inputs = html_input(page) #获取隐域的常量
	li = html_li(page) #获取<li>标签里的视频参数
	global Copyright
	Copyright = inputs['copyright']
	num = int(len(li)*rate/100) #将进度转化为要刷的视频数量
	print('开始刷课...')
	for each in li.values(): #用for循环遍历每一个视频
		#刷到相应的视频数量时跳出循环
		if num == 0:break
		if each['watchstate'] != '1': #判断改视频观看状态，若不等于1(未观看or没看完)，则进行刷课
			temp = inputs
			temp.update(each) #更新字典，将视频参数字典更新到常量字典里面
			if temp['_lessonvideoid'] == None:temp['_lessonvideoid'] = '0'
			#调用函数发包
			studied_Id = studiedId(temp)
			if studied_Id == 1:return(1)
			cache_status = saveCache(temp,studied_Id)
			database_status = saveDatabase(temp,studied_Id)
			if cache_status == 200 and database_status == 200:
				print(temp['_name'],'\t','OK')
			else:
				print(temp['_name']+'\t'+'FAILED:',cache_status,'    ',database_status)
			time.sleep(speed) #刷课时间间隔
		num -= 1
	print('该门课程刷课结束,请打开下一门课程的视频页面...')
	return(0)

if __name__ == '__main__':#入口函数
	options = Options()
	options.add_argument('--disable-gpu')
	browser = webdriver.Firefox(firefox_options=options)
	session = requests.Session() #建立会话
	print('正在打开登录页面,请自行输入账号密码并登录...')
	browser.get(entrance) #打开登录页面
	#循环刷课
	while True:
		#获取刷课进度
		while True:
			try:
				rate = int(input('\n\n请输入该门课程的刷课进度(0-100):')) #输入要刷到的进度，默认50%
			except:
				exit()
			if 0 < rate <= 100:break
			print('输入有误,请重新输入!')
		html = load() #调用load()获取cookie和html页面
		if html == 1:continue
		main_return = main(html,rate) #传入页面和进度，进入主函数
		if main_return == 1:continue
