# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import requests
import time
import pymongo
import re

from categoryUrl_list import categoryUrl_list

from multiprocessing import Pool

# 考虑函数中都要调用这部分的数据库，因此在.py文件最开始就申明了如下代码
# 建立数据库ganji
client = pymongo.MongoClient('localhost',27017)
ganji = client['ganji']

# 根据不同的分类插入不同类别信息的表格
# 注意exec命令的使用，让字符串变为了变量名
for category in categoryUrl_list:
	exec "%s = ganji['%s']" %(category['title_name'],category['title_name'])


def getCategory_url(category_url, category_title, page=1, who_sell=1):
	"""
	将指定分类的商品详情页的url插入数据库中
	:param category_url: 指定分类的整体页面url
	:param category_title: 分类名
	:param page: 设置翻页页码，注意这里的页面是从1开始的，而不是0
	:param who_sell: '1'表示个人，'2'表示商家
	:return:将指定分类的商品详情页的url插入数据库中
	"""
	# 重构分类的整体页面url，在页码为1的代码不符合统一的规则，因此需要再设置
	if page == 1:
		category_url = '{0}a{1}'.format(category_url,str(who_sell))
	elif page > 1:
		category_url = '{0}a{1}o{2}'.format(category_url,str(who_sell),str(page))
	else:
		print 'Wrong Page Number'


	# 解析页面
	response = requests.get(category_url)
	soup = BeautifulSoup(response.text,'lxml')

	# 状态码，用于判断一个分类是否爬取完成
	stat_code = '200'

	if soup.select('div.noinfo'):
		stat_code = '404'

	# CSS选择器规则列表，增加这个列表主要是为了满足扩充CSS选择器的库，后面可以考虑做成一个类
	cssSelector = ['table tbody tr td.t a','tbody tr td.t a'
				   'table tbody tr td.t a','p.infor-title a.list-title.f14',
				   'dd.feature div ul li a','table tbody tr td.t a',
				   'div.layoutlist dl dt div > a']

	# 对需要反复调用的量item_list进行列表初始化（主要是解决一个报错的BUG）
	item_list = []

	# 根据个人与商家页面结构的不同选择不同的CSS选择器，1表示个人，2表示商家
	if who_sell == 1:
		for cssSelector in cssSelector:
			# 这个地方不能使用简便写法 A if C else B,会报错
			if soup.select(cssSelector):
				item_list = soup.select(cssSelector)

	elif who_sell == 2:
		item_list = soup.select('dd.feature div ul li > a')
	else:
		print '错误的who_sell信息'

	# 数据库写入
	for item in item_list:
		# 通过span标签去除推广广告，同时修复了BUG，即使在两个类别中的不能使用span标签
		if not item.select('span') or category_title in ['xuniwupin','xianzhilipin']:
			# 将商品详情页url信息插入到数据库
			# print item['href'].split('?')[0]
			if 'http' in item['href'].split('?')[0]:
				exec "%s.insert_one({'item_url':item['href'].split('?')[0]}) if item['href'] else None" %(category_title)
			else:
				exec "%s.insert_one({'item_url': 'http://sh.ganji.com' + item['href'].split('?')[0]}) if item['href'] else None" % (category_title)

	return stat_code

def getDetailInfo(detail_url):

    #解析网页
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.text,'lxml')

    #
    title = soup.title.text

    # 处理详情页中，在select之后得到的是一个个数为1的列表，因此需要加一个[0]来提取元素
    seller_name = soup.select('p.personal_name')[0].get_text()
    seller_joinTime_str = soup.select('p.personal_chengjiu')[0].get_text()

    # 利用正则表达式获取中文字段中的数字信息
    seller_joinTime = int(re.findall('[0-9]+',seller_joinTime_str)[0])

    view_count = int(re.findall('[0-9]+',soup.select('span.look_time')[0].get_text())[0])
    wantBuy_count = int(re.findall('[0-9]+',soup.select('span.want_person')[0].get_text())[0])

    region = soup.select('div.palce_li span i')[0].get_text() if soup.select('div.palce_li span i') else None

    price = soup.select('span.price_now i')[0].get_text()

    tags = list(soup.select('div.biaoqian_li')[0].stripped_strings) if soup.select('div.biaoqian_li') else None

    # 将选取的数据存至dic中，并插入数据库中
    item_info_dic = {
        'title':title,
        'seller_name':seller_name,
        'seller_joinTime(days)':seller_joinTime,
        'view_count':view_count,
        'wantBuy_count':wantBuy_count,
        'region':region,
        'price':price,
        'tags':tags
    }

	# 数据入库
	# databaseName.insert_one(item_info_dic)


def getCategoryAll_url(categoryUrl_list):
	"""
	这个函数，主要是为了满足使用map函数的结构，pool.map(getCategoryAll_url,categoryUrl_list)
	:param categoryUrl_list: 各个类目的字典列表信息
	:return:
	"""

	# 将categoryUrl_list字典结构分离一下
	category_url = categoryUrl_list['href']
	category_title = categoryUrl_list['title_name']

	# 构建数据表
	exec "%s = ganji['%s']" % (category_title, category_title)

	# for who_sell in xrange(1,3,1):
	# 选择爬取每个类目的页码最大数量
	for page in xrange(1, 100, 1):
		# 调用geeCategory_url
		stat_code = getCategory_url(category_url,category_title, page, who_sell=1)

		# 根据状态码stat_code判断是否跳出循环，并且在页码中间还会存在有间断现象
		if '404' in stat_code and page > 100:
			break

def postProcess_count(categoryUrl_list):
	"""
	输出一些关于数据库的信息，以及在添加了CSS选择器列表之后，重新下载url_list
	:param categoryUrl_list:
	:return: 剩余CSS选择器未匹配的字典类目
	"""
	# 用于统计总数的变量
	sumAll = 0

	# 用于保存计数中为0的类目
	rest_category = []

	for category in categoryUrl_list:

		# 通过数据库的操作函数.find().count()统计具体表中的元素数量
		exec "count = %s.find().count()" %(category['title_name'])

		print category['title_name'] + ': ' + str(count)

		if count == 0:
			rest_category.append(category)

		sumAll += count

	print '总的商品数量为：' + str(sumAll)

	print '剩余的可能未识别的商品类别数量为 ' + len(rest_category)

	print '具体类别如下：'

	# 打印出计数为0的类别
	for item in rest_category:
		print '\t' + item['title_name']

	return rest_category

def getAllDetailInfo(itemUrl_list):
	pass

if __name__ == '__main__':

	# 所线程功能
	pool = Pool()

	# # 得到各个类目的所有商品详情页url的数据表
	# pool.map(getCategoryAll_url,categoryUrl_list)
    #
	# # 得到未被成功下载的类别列表，在调整完CSS选择器之后，准备重新下载
	# rest_category = postProcess_count(categoryUrl_list)
    #
	# # 在添加完CSS选择器列表元素之后，重新下载url_list
	# pool.map(getCategoryAll_url,rest_category)

	for category_detail in categoryUrl_list:

		exec "detail_url_list = %s.find()" %(category_detail['title_name'])

		for item in detail_url_list:
			print item['item_url']

		# pool.map(getDetailInfo,detail_url_list)
















