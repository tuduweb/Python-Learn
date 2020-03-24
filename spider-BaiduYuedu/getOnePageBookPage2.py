import requests
import chardet
import re
import urllib.parse
import io
import sys
import time
import random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

siteUrl = 'https://yuedu.baidu.com/book/list/0?fr=indextop'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}

categoryUrl = urllib.parse.urljoin(siteUrl,'/book/list/9003?od=0&show=0&pn=20')
cnt = 0
print("当前页面:%s" % categoryUrl)

response = requests.get(categoryUrl,headers=headers,params=None)
pageStr = str(response.content, encoding = "gbk")
with open('./category-test.html','w+') as f:
    f.write(pageStr)
    f.close()

#pattern = re.compile('<div class="book .*?<a.*?data-src="(.*?)" alt="(.*?)".*?href="(.*?)".*?author">(.*?)</span>.*?<span>￥</span>(.*?)\n</span>.*?</div>', re.S)
#books = re.findall('<div class="book .*?<a.*?data-src="(.*?)" alt="(.*?)".*?href="(.*?)".*?author">(.*?)</span>.*?<span>￥</span>(.*?)\n</span>.*?</div>', pageStr, re.S)

books = re.findall('<div class="book .*?data-src="(.*?)" alt="(.*?)".*?href="(.*?)".*?author">(.*?)</span>.*?</div>', pageStr, re.S)

print(len(books))

for book in books:
    print(book[0])
    print(book[1])
    print(book[2])
    print(book[3])
    print("==================================")


## 下一页测试 <div class="pager-inner">

nextPageUri = re.search('href="([^"]*?)" class="next"',pageStr)
print(nextPageUri.group(1))

if nextPageUri:
    categoryUrl = urllib.parse.urljoin(siteUrl,nextPageUri.group(1))



cnt = cnt + 1

