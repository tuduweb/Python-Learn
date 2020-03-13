import requests
import re
import io
import sys
from urllib.parse import urlparse, urljoin

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
