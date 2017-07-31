# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
import requests
import time
import pymongo
import re

detail_url = 'http://zhuanzhuan.ganji.com/detail/891468740215095307z.shtml'

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





