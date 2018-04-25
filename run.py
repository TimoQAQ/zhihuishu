#Author : TimoQAQ
#Author's QQ : 2190778650
#Version ：1.1
#Date : 2018-4-20
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

temp = ''
copyright = ''
speed = 0.2 #刷课时间间隔，默认200毫秒

#切换到当前页面
def convert():
	time.sleep(3)
	windows = browser.window_handles
	browser.switch_to.window(windows[-1])

#加载网页，获取cookies和页面
def load(u,p,n):
	url = 'https://passport.zhihuishu.com/login?service=http://online.zhihuishu.com/onlineSchool/'
	browser.get(url)
	browser.implicitly_wait(10) #隐式等待页面加载
	
	#登录页面
	try:
		time.sleep(3)
		browser.find_element_by_id('lUsername').send_keys(u) #模拟输入用户名
		browser.find_element_by_id('lPassword').send_keys(p) #模拟输入密码
		browser.find_element_by_css_selector('.wall-sub-btn').click() #模拟点击登录按钮
		print('登录成功...')
	except:
		print('登录失败!')
		exit()
	
	#选择一门课程
	try:
		time.sleep(3) #可加大参数
		browser.find_elements_by_css_selector('.courseImgs')[n].click() #点击对应课程
		convert()
		print('进入视频页面...')
	except:
		#关闭弹出界面
		try:
			browser.find_element_by_id('close_windowa').click() #点击关闭弹出界面
			time.sleep(1) #可加大参数
			print('关闭弹出界面...')
			browser.find_elements_by_css_selector('.courseImgs')[n].click() #点击对应课程
			convert()
			print('进入视频页面...')
		except:
			print('进入视频页面失败!')
			exit()
		
	#保存cookies到requests.session
	cookie = ["'" + item["name"] + "':'" + item["value"] + "'" for item in browser.get_cookies()]
	cookiestr = ','.join(item for item in cookie)
	cookiestr = '{' + cookiestr + '}'
	session.cookies = requests.utils.cookiejar_from_dict(eval(cookiestr), cookiejar=None, overwrite=True)
	
	#由于不知道怎么将selenium的cookies格式转换为带域名的ccookiejar,所以我们要为csrftoken、SERVERID添加域名
	token = session.cookies['csrftoken']
	serverid = session.cookies['SERVERID']
	session.cookies.set('csrftoken', None)
	session.cookies.set('SERVERID', None)
	session.cookies.set('csrftoken', token, path='/', domain='study.zhihuishu.com')
	session.cookies.set('SERVERID', serverid, path='/', domain='study.zhihuishu.com')
	
	print('成功获取cookie...')
	print('返回页面...')
	return (browser.page_source)

#传入一个标准参数字典,返回studiedId
def studiedId(params):
	t = int(round(time.time() * 1000))
	url = 'http://study.zhihuishu.com/json/learning/prelearningNote?time=' + str(t)

	header = {
	'Host': 'study.zhihuishu.com',
	'Connection': 'keep-alive',
	'Accept': '*/*',
	'Origin': 'http://study.zhihuishu.com',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': 'http://study.zhihuishu.com/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
	}
	
	data = {
	'rid':params['rid'],
	'studentCount':'1',
	'lessonId':params['lessonId'],
	'PCourseId':params['PCourseId'],
	'chapterId':params['chapterId'],
	'lessonVideoId':'',
	'userId':params['userId'],
	'videoId':params['videoId'],
	'studyStatus':''
	}
	
	response = session.post(url, headers = header, data = data) #POST数据包
	return(re.search(r'"id":([0-9]*),"is',response.text).group(1)) #匹配response里的studiedId并返回

#存入缓存
def saveCache(params):
	t = int(round(time.time() * 1000))
	url = 'http://study.zhihuishu.com/json/learning/saveCacheIntervalTime?time=' + str(t)
	
	if params['lessonvideoid'] != None:
		lessonVideoId = params['lessonvideoid']
	else:
		lessonVideoId = '0'
		
	global temp,copyright
	temp = base64.b64encode(studiedId(params).encode('utf-8')) #加密studiedId生成__learning_token__
	copyright = params['copyright']
	
	header = {
	'Host': 'study.zhihuishu.com',
	'Connection': 'keep-alive',
	'Accept': '*/*',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': 'http://study.zhihuishu.com/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	#'Referer': 'http://study.zhihuishu.com/learning/videoList;jsessionid='+session.cookies['JSESSIONID']+'?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
	}
	
	data = {
	'rid':params['rid'],
	'chapterId':params['chapterId'],
	'courseId':params['courseId'],
	'lessonId':params['lessonId'],
	'learnTime':params['videosize'],
	'studyTotalTime':studyTime(params['videosize']),
	'__learning_token__':temp,
	'studyStatus':'',
	'videoId':params['videoId'],
	#'watchPoint':'0%2C1%2C93%2C93',
	'ev':encode([params['rid'], params['lessonId'], lessonVideoId, params['videoId']]),
	'csrfToken':session.cookies['csrftoken'],
	'lessonVideoId':params['lessonvideoid']
	}
	
	response = session.post(url, headers = header, data = data)
	print('saveCache:' + params['name'] + '   ',response.status_code)

#存入数据库
def saveDatabase(params):
	t = int(round(time.time() * 1000))
	url = 'http://study.zhihuishu.com/json/learning/saveDatabaseIntervalTime?time=' + str(t)
	
	if params['lessonvideoid'] != None:
		lessonVideoId = params['lessonvideoid']
	else:
		lessonVideoId = '0'
	
	header = {
	'Host': 'study.zhihuishu.com',
	'Connection': 'keep-alive',
	'Accept': '*/*',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': 'http://study.zhihuishu.com/learning/videoList?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	#'Referer': 'http://study.zhihuishu.com/learning/videoList;jsessionid='+session.cookies['JSESSIONID']+'?courseId=' + params['courseId'] + '&rid=' + params['rid'],
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
	}
	
	data = {
	'__learning_token__':temp,
	'studiedLessonDto.learnTime':params['videosize'],
	'studiedLessonDto.studyTotalTime':studyTime(params['videosize']),
	'studiedLessonDto.playTimes':'35',
	'studiedLessonDto.recruitId':params['rid'],
	'studiedLessonDto.lessonVideoId':'',
	'studiedLessonDto.lessonId':params['lessonId'],
	'studiedLessonDto.videoId':params['videoId'],
	'studyStatus':'',
	'studiedLessonDto.sourseType':'1',
	'ev':encode([params['rid'], params['lessonId'], lessonVideoId, params['videoId'], '1']),
	'csrfToken':session.cookies['csrftoken']
	}
	
	response = session.post(url, headers = header, data = data)
	print('saveDatabase:' + params['name'] + '   ',response.status_code)

#输入视频长度,返回毫秒级时间戳
def studyTime(videosize):
	std_time = '1970-01-01 08'
	temp = std_time + videosize[2:]
	date = time.mktime(time.strptime(temp,'%Y-%m-%d %H:%M:%S'))
	return(int(date))

#传入一个html页面,返回一个input_hidden字典
def const_param(page):
	nums = {}
	soup = BeautifulSoup(page, 'html.parser')
	input = soup.find_all('input',attrs={'type':'hidden'}) #BeautifulSoup匹配所有type为hidden的<input>标签
	
	#生成常量字典
	for each in input:
		nums[each.get('id')] = each.get('value')
	
	return(nums)

#传入一个html页面,返回一个视频参数的二维字典{videoId:{},videoId:{}}
def li_param(page):
	nums = {}
	soup = BeautifulSoup(page, 'html.parser')
	li = soup.find_all('li',id=re.compile('video-[0-9]{4,8}')) #BeautifulSoup匹配对应视频的<li>标签
	
	#加入视频时间，并生成视频字典
	for each in li:
		span = each.find('span', attrs={'class':'time fl'}).text
		nums[each.get('_videoid')] = {'videoId':each.get('_videoid'),'name':each.get('_name'),'watchstate':each.get('watchstate'),'chapterId':each.get('_chapterid'),'lessonId':each.get('_lessonid'),'videosize':span,'lessonvideoid':each.get('_lessonvideoid')}
	
	return(nums)

#由JS翻译过来的加密函数,返回ev参数
def encode(param):
	a = ''
	f = ''
	d = 0
	string=copyright
	
	for c in range(len(param)):
		a += param[c]+';'
	a=a[:len(a)-1];
	
	for c in range(len(a)):
		d = ord(a[c])^ord(string[c%len(string)])
		e = str(hex(d))[2:]
		if len(e) < 2 :
			e ='0'+e
		f += e
	
	return(f)

#执行函数
def action(page,rate):
	input = const_param(page) #获取隐域的常量
	li = li_param(page) #获取<li>标签里的视频参数
	num = int(len(li)*rate/100) #将进度转化为要刷的视频数量
	print('开始刷课...')
	
	for each in li.values(): #用for循环遍历每一个视频
		
		#刷到相应的视频数量时跳出循环
		if num == 0:
			break
		num -= 1
		
		if each['watchstate'] != '1': #判断改视频观看状态，若不等于1(未观看or没看完)，则进行刷课
			temp = input
			temp.update(each) #更新字典，将视频参数字典更新到常量字典里面
			
			#调用函数发包
			saveCache(temp)
			saveDatabase(temp)
			time.sleep(speed) #刷课时间间隔
		
	print('刷课结束!')

#入口函数
if __name__ == '__main__':
	userid = input('请输入账号:') #输入账户(手机号)
	password = input('请输入密码:') #输入密码
	number = int(input('请输入课程号:')) - 1 #获取网课号，比如要刷第一门网课就输入1
	try:
		rate = int(input('请输入刷课进度(默认50%):')) #输入要刷到的进度，默认50%
	except:
		rate = 50
	
	options = Options()
	#options.add_argument('-headless')
	options.add_argument('--disable-gpu')
	browser = webdriver.Firefox(firefox_options=options)
	
	session = requests.Session() #建立会话
	html = load(userid,password,number) #调用load()获取cookie和html页面
	action(html,rate) #传入页面和进度，进入执行函数
	
	
#关闭会话
#关闭浏览器
#刷课验证函数


