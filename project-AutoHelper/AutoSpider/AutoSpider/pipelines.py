# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

import scrapy
from itemadapter import ItemAdapter


class AutospiderPipeline:
    current_file_num = 0
    download_path = 'M:/default_download/'

    def __init__(self, download_path):
        self.download_path = download_path

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            download_path=crawler.settings.get("FILES_STORE")
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        print('Pipeline received  %s' % item.get('title'))

        # 每次提交的json保存到本地
        # 解析附件
        attachments = adapter.get('attachments')
        if attachments is not None:
            print('Attachment Files:')
            for file in attachments:
                print('[%d] %s %s size:%d'
                      % (self.current_file_num, file.get('title'), file.get('ufile_key'), int(file.get('ufile_size'))))
                filesize = int(file.get('ufile_size'))
                if True or filesize <= 140496:  # bypass
                    # https://file.learnerhub.net/uploads-1610436699331/filename.fileext?attname=filename.fileext
                    fileuri = file.get('ufile_key')
                    filename = fileuri.split('/')[-1]
                    print(filename)
                    if filename is not None:
                        adapter['file_urls'].append('https://file.learnerhub.net/%s?attname=%s' % (fileuri, filename))
                self.current_file_num += 1
                pass

            #self.download_path
            path = os.path.join(self.download_path, str(adapter.get('post_id')))
            if os.path.exists(path) is False:
                os.makedirs(path)

            print(path)
            with open('%s/info.txt' % path, 'a') as f:
                f.write(str(adapter.get('json_data')))
                f.close()
            json_data = json.dumps(adapter.get('json_data'))

            with open('%s/info.json' % path, 'a') as f:
                f.write(json_data)
                f.close()

        return item


import os
from urllib.parse import urlparse

from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem
from urllib.parse import parse_qs, urlparse, urlencode, unquote, unquote_plus, quote, quote_plus


class MyFilesPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        for url in item['file_urls']:
            yield scrapy.Request(url, meta={'item': item})

    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta.get('item', 'test')
        print('file download')
        # unquote_plus 将uri编码转换成正常字符
        post_id = item.get('post_id', '0')
        #return None
        return 'files/' + str(post_id) + '/' + unquote_plus(os.path.basename(urlparse(request.url).path))

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('File Downloaded Failed')
        return item
