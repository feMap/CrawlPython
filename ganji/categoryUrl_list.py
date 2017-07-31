# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import requests

base_url = 'http://sh.ganji.com'

# 二手市场分类列表
categoryUrl_list = []

response = requests.get(base_url + '/wu/')
response.encoding = ('utf8')
soup = BeautifulSoup(response.text,'lxml')

# CSS选择器
title_info = soup.select('li  div  dl  dt a')

# 解析页面，将分类页面信息插入categoryUrl_list
for title_info in title_info:
	if title_info['href']:
		title_info_list ={
			# 'title_name':title_info.get_text(),
			'title_name':title_info['href'].split('/')[1],
		 	'href':base_url + title_info['href']
		}

		categoryUrl_list.append(title_info_list)

# print categoryUrl_list[9]['title_name']