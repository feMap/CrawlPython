# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pymongo

# 建立数据库ganji
client = pymongo.MongoClient('localhost',27017)
ganji = client['ganji']

# 根据不同的分类插入不同类别信息的表格
shouji = ganji['shouji']

# 建立数据库ganji
client = pymongo.MongoClient('localhost',27017)
test = client['test']

sheetName_list=['femap','Alice']


exec "%s = test['%s']" %(sheetName_list[0],sheetName_list[1])

exec "%s.insert_one({'femap':'No1'})" %(sheetName_list[0])

# print femap