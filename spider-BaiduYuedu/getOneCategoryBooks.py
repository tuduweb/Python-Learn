import requests
import chardet
import re
from urllib.parse import urlparse, urljoin
import io
import sys
import time
import random

import csv

csvHeaders = ['bookUri','bookName','author','price','hits','coverImgUrl','publishedTime','lastUpdateTime']

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

siteUrl = 'https://yuedu.baidu.com/book/list/0?fr=indextop'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}

def GetBookDetail( uri ):
    print("页面详情:%s" % uri)
    bookUrl = urljoin(siteUrl,uri)
    #print(bookUrl)
    response = requests.get(bookUrl,headers=headers,params=None)
    pageStr = str(response.content, encoding = "gbk")
    matchedList = []
    matchedList.append(re.search('<meta itemprop="dateUpdate" content="(.*?)">',pageStr))
    matchedList.append(re.search('<meta itemprop="datePublished" content="(.*?)">',pageStr))
    matchedList.append(re.search('class="doc-info-read-count">(.*?)人在读',pageStr))
    matchedList.append(re.search("d.set\('confirm_price', '(.*?)'\);",pageStr))
    data = []
    for matched in matchedList:
        if matched:
            data.append(matched.group(1))
            #print(matched.group(1))
        else:
            data.append("")
    return data

categoryUrl = urljoin(siteUrl,'/book/list/9003')
cnt = 0
bookCnt = 1
while (categoryUrl != 0) and (cnt < 2):
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("当前页面:%s" % categoryUrl)

    response = requests.get(categoryUrl,headers=headers,params=None)
    pageStr = str(response.content, encoding = "gbk")
    with open('./category-%d.html' % cnt,'w+') as f:
        f.write(pageStr)
        f.close()

    #pattern = re.compile('<div class="book .*?<a.*?data-src="(.*?)" alt="(.*?)".*?href="(.*?)".*?author">(.*?)</span>.*?<span>￥</span>(.*?)\n</span>.*?</div>', re.S)
    books = re.findall('<div class="book .*?data-src="(.*?)" alt="(.*?)".*?href="(.*?)".*?author">(.*?)</span>.*?</div>', pageStr, re.S)

    for book in books:
        #print(book[0])#书的图片地址
        #print(book[1])#书的标题
        #print(book[2])#书的地址
        #print(book[3])#作者名字
        data = GetBookDetail(book[2])
        #print(data)#data [0]->更新日期 [1]->发表日期 [2]->点击量 [3]->价格
        print("[%s](%s)图书：%s 作者<%s> 点击量[%s] 上次更新:%s" % (bookCnt,urlparse(book[2]).path.split("/")[-1],book[1],book[3],data[2],data[0]))
        #csvHeaders = ['bookUri','bookName','author','price','hits','coverImgUrl','publishedTime','lastUpdateTime']
        row = [urlparse(book[2]).path.split("/")[-1],book[1],book[3],data[3],data[2],book[0],data[1],data[0]]
        with open('database.csv','a',newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(row)
        #print(row)
        bookCnt = bookCnt + 1
        print("==================================")

    ## 下一页测试 <div class="pager-inner">

    nextPageUri = re.search('href="([^"]*?)" class="next"',pageStr)
    print(nextPageUri.group(1))

    if nextPageUri:
        categoryUrl = urljoin(siteUrl,nextPageUri.group(1))

    sleeptime = random.randint(100, 400)
    print("sleep %f" % (sleeptime/1000))
    time.sleep(sleeptime/1000)

    cnt = cnt + 1

