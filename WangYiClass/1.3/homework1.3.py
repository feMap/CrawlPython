# coding: utf-8

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

import requests
from bs4 import BeautifulSoup
import time
import pprint
import re

# url = 'http://bj.xiaozhu.com/fangzi/12163452701.html'

def getHouseInfo_dic(detailPage_url):
	"""
	根据url获取小猪短租的详情页面的房屋信息
	:param url: 详情页的链接地址
	:return: 返回详情页中的房屋信息和房东信息的字典
	"""
	response = requests.get(detailPage_url)
	soup = BeautifulSoup(response.text,'lxml')

	'''
	# 房屋信息
	titles = soup.select('div.con_l > div.pho_info > h4')
	position = soup.select('div.con_l > div.pho_info > p > span')
	pay = soup.select('#pricePart > div.day_l > span')
	imgs = soup.select('#curBigImage')

	# 房东信息
	fangdong = soup.select('#floatRightBox > div.js_box.clearfix > div.member_pic > a > img')
	gender = soup.select('#floatRightBox > div.js_box.clearfix > div.w_240 > h6 > span')
	fangdong_name = soup.select('#floatRightBox > div.js_box.clearfix > div.w_240 > h6 > a')
	'''

	# 获取单页面中的所有信息
	houseInfo_dict = {
		# 房屋信息
		'titles' : soup.select('div.con_l > div.pho_info > h4')[0].get_text(),
		'position' : soup.select('div.con_l > div.pho_info > p > span')[0].get_text(),
		'pay' : soup.select('#pricePart > div.day_l > span')[0].get_text(),
		'imgs' : soup.select('#curBigImage')[0].get('src'),

		# 房东信息
		'fangdong' : soup.select('#floatRightBox > div.js_box.clearfix > div.member_pic > a > img')[0].get('src'),
		'gender' : genderTransform(str(soup.select('#floatRightBox > div.js_box.clearfix > div.w_240 > h6 > span')[0])),
		'fangdong_name' : soup.select('#floatRightBox > div.js_box.clearfix > div.w_240 > h6 > a')[0].get_text()
	}
	
	return houseInfo_dict

def genderTransform(gender):
	"""
	因为这个字段中，是以一个icon作为性别的识别，因此利用正则表达式中的re.search匹配girl字段
	:param gender:待解析的标签内容
	:return:性别字符（'Female','Male'）
	"""
	if re.search(r'girl',gender):
		return 'Female'
	else:
		# 这个
		return 'Male'

def get_pageurl_list(base_url):
	"""
	获取详情页url的列表
	:param base_url:基础页面的url
	:return: 返回具体详情页的链接
	"""
	response = requests.get(base_url)
	soup = BeautifulSoup(response.text,'lxml')

	hrefInfo_list = soup.select('#page_list > ul > li > a')

	for hrefpage in hrefInfo_list:
        pageurl_list.append(hrefpage.get('href'))

def output_txt(path,detailPageInfo):
    """
    将详情页列表信息格式化输出到txt文件
    :param path: 包含txt文件名的文件路径
    :param detailPageInfo: 详情页信息列表
    :return: None
    """

    num = 0

    with open(path,'w') as f:
        f.write('<' + '-'*20 + '>\n')

        for file in detailPageInfo:
            num += 1
            # 写入
            f.write('<' + '-'*8 + str(num) + '-'*8 + '>\n')
            for key, value in file.items():
                f.write(key + ':' + value + '\n')

            f.write('<' + '-' * 20 + '>\n')


if __name__ == "__main__":

    pageurl_list = []

    base_url = 'http://bj.xiaozhu.com/'

    # 获取之前的前300条的房屋详情页url列表

    for i in xrange(1,20):

        print '正在爬取 Page{0} ...'.format(i)

        url = 'http://bj.xiaozhu.com/search-duanzufang-p' + str(i) +'-0/'.format(i)

        get_pageurl_list(url)

        if len(pageurl_list) >= 100:
            break

    print '房屋url列表爬取完毕'


    detailPageInfo = []

    for url in pageurl_list:
        print '正在爬取详情页 {0}'.format(url)
        detailPageInfo.append(crawl(url))

    print "详情页爬取完毕"

    # 输出爬取信息到txt中
    output_txt('xiaozhu300.txt',detailPageInfo)



