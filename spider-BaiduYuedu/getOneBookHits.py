import requests
import chardet
import re
import urllib.parse
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

siteUrl = 'https://yuedu.baidu.com/book/list/0?fr=indextop'

bookUrl = urllib.parse.urljoin(siteUrl,'/ebook/81a5b78abe23482fb5da4c48?fr=booklist')

print(bookUrl)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}

response = requests.get(bookUrl,headers=headers,params=None)
#print(chardet.detect(response.content))
#print(response.content)

#print(result)
#print(response.text.encode('GB2312','ignore').decode('GB2312'))

pageStr = str(response.content, encoding = "gbk")
#内容保存测试
with open(r'./book.html','w+') as f:
    f.write(pageStr)
    f.close()


data = []
data.append(re.search('<meta itemprop="dateUpdate" content="(.*?)">',pageStr))
data.append(re.search('<meta itemprop="datePublished" content="(.*?)">',pageStr))
data.append(re.search('class="doc-info-read-count">(.*?)人在读',pageStr))
data.append(re.search('class="numeric">(.*?)</span>',pageStr))
data.append(re.search("d.set\('confirm_price', '(.*?)'\);",pageStr))

for matched in data:
    print(matched.group(1))

## 判断是否存在标签
labelsMatched = re.search('<div class="content"(.*?)</div>', pageStr,re.S)
if labelsMatched:
    labels = re.findall('<a.*?title="(.*?)">', labelsMatched.group(0), re.S)
    print(labels)

#test = re.findall(pattern, pageStr)



