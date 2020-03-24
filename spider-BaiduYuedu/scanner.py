import requests
import re
import io
import sys
from urllib.parse import urlparse, urljoin
import chardet
import csv
import time
import random

### for Chinese output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')


siteUrl = 'https://yuedu.baidu.com/book/list/0?fr=indextop'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}

response = requests.get(siteUrl,headers=headers,params=None)
#print(chardet.detect(response.content))
#print(response.content)

#print(result)
#print(response.text.encode('GB2312','ignore').decode('GB2312'))

str = str(response.content, encoding = "gbk")

with open(r'./content.html','w+') as f:
    f.write(str)
    f.close()

#result = re.match(r'<a.*?href=".*?">(.*?)</a>',r'<a title="gbk" href="/book/list/6032">gbk</a>')

pattern = re.compile('<li>.*?<a.*?title="(.*?)".*?href="(.*?)">.*?</a>.*?</li>', re.S)

#categories = re.findall(pattern, str)
#print(categories)






##<div class="tab-cate-hd">

## mainCategories = re.findall('<div class="tab-cate-hd">\n<a href="(.*?)">(.*?)</a>\n<b class="ic ic-arrow"></b>',str,re.S)

mainHtmlBlocks = re.findall('<div class="cate-menu-box cate-menu-box-more cate-menu-box-index-(.*?)</ul>\n</div>\n</div>', str, re.S)

#print(mainHtmlBlocks)

cateData = []

### build two-level categories
for block in mainHtmlBlocks:
    searched = re.search('<div class="tab-cate-hd">\n<a href="(.*?)">(.*?)</a>\n<b class="ic ic-arrow"></b>',block,re.S)
    if searched:
        cateData.append([ int(urlparse(searched.group(1)).path.split("/")[-1]) , searched.group(2), searched.group(1), 0]) ## data[2] value 0 <-> top level
        cateInBlock = re.findall('<li>.*?<a.*?title="(.*?)".*?href="(.*?)">.*?</a>.*?</li>', block, re.S)
        for cate in cateInBlock:
            cateData.append([ int(urlparse(cate[1]).path.split("/")[-1]) , cate[0], cate[1], int(urlparse(searched.group(1)).path.split("/")[-1]) ])

if len(cateData) > 0:
    print("OK!Get %d Classified Items" % len(cateData))
else:
    print("ERR!")



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


for cate in cateData:
    ## cate[0]->id 1->title 2->uri 3->parentID
    if cate[3] == 0:
        continue
    categoryUrl = urljoin(siteUrl,cate[2])
    categoryScannedPageCnt = 0
    while (categoryUrl != 0) and (categoryScannedPageCnt < 2):
        response = requests.get(categoryUrl,headers=headers,params=None)
        pageStr = str(response.content, encoding = "gbk")
        print(categoryUrl)

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
            row = [urlparse(book[2]).path.split("/")[-1],book[1], cate[0],book[3],data[3],data[2],book[0],data[1],data[0]]
            with open('database.csv','a',newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(row)
            #print(row)
            bookCnt = bookCnt + 1
            print("==================================")

        nextPageUri = re.search('href="([^"]*?)" class="next"',pageStr)
        print(nextPageUri.group(1))
        
        ## if exist next page
        if nextPageUri:
            categoryUrl = urljoin(siteUrl,nextPageUri.group(1))

        sleeptime = random.randint(100, 400)
        print("sleep %f" % (sleeptime/1000))
        time.sleep(sleeptime/1000)

        categoryScannedPageCnt = categoryScannedPageCnt + 1
