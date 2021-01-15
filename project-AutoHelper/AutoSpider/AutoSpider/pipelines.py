# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

import scrapy
from itemadapter import ItemAdapter
from AutoSpider.items import AutospiderItem


class AutospiderPipeline:
    current_file_num = 0
    download_path = 'M:/default_download/'

    def __init__(self, download_path, mongourl, mongoport, mongodb):
        self.download_path = download_path
        self.mongo_uri = mongourl
        self.mongo_port = mongoport
        self.mongo_db = mongodb

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            download_path=crawler.settings.get("FILES_STORE"),
            mongourl=crawler.settings.get("MONGO_URL"),
            mongoport=crawler.settings.get("MONGO_PORT"),
            mongodb=crawler.settings.get("MONGO_DB")
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

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

            # insert into database
            if isinstance(item, AutospiderItem):
                #TODO: 用for方法循环改动
                if self.db['lhub_attachment'].find({'post_id': item['post_id']}).count() == 0:
                    record_id = self.db['lhub_attachment'].insert_one({
                        'post_id': adapter.get('post_id'),
                        'title': adapter.get('title'),
                        'description': adapter.get('description'),
                        'owner_id': adapter.get('owner_id'),
                        'attachments': adapter.get('attachments'),
                        'updated_time': adapter.get('updated_time'),
                    }).inserted_id
                    print("Attachment %d insert %s!" % (item['post_id'], record_id))
                else:
                    print("Attachment %d exist!" % item['post_id'])

        return item


import pymongo
from AutoSpider.items import TopicItem
from AutoSpider.items import CommentItem
class CommentsPipeline:
    # download_path = 'M:/default_download/'

    def __init__(self, mongourl, mongoport, mongodb):
        self.mongo_uri = mongourl
        self.mongo_port = mongoport
        self.mongo_db = mongodb

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongourl=crawler.settings.get("MONGO_URL"),
            mongoport=crawler.settings.get("MONGO_PORT"),
            mongodb=crawler.settings.get("MONGO_DB")
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        print('Topic Pipeline')
        adapter = ItemAdapter(item)
        if isinstance(item, TopicItem):
            if self.db['lhub_topic'].find({'topic_id': item['topic_id']}).count() == 0:
                record_id = self.db['lhub_topic'].insert_one(item).inserted_id
                print("Topic %d insert %s!" % (item['topic_id'], record_id))
            else:
                print("Topic %d exist!" % item['topic_id'])
        elif isinstance(item, CommentItem):
            if self.db['lhub_comment'].find({'comment_id': item['comment_id']}).count() == 0:
                record_id = self.db['lhub_comment'].insert_one(item).inserted_id
                print("Comment %d insert %s!" % (item['comment_id'], record_id))
            else:
                print("Comment %d exist!" % item['comment_id'])
        return item

from AutoSpider.items import UserItem
class UserPipeline:
    def __init__(self, mongourl, mongoport, mongodb):
        self.mongo_uri = mongourl
        self.mongo_port = mongoport
        self.mongo_db = mongodb

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongourl=crawler.settings.get("MONGO_URL"),
            mongoport=crawler.settings.get("MONGO_PORT"),
            mongodb=crawler.settings.get("MONGO_DB")
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            if self.db['lhub_user'].find({'user_id': item['user_id']}).count() == 0:
                record_id = self.db['lhub_user'].insert_one(item).inserted_id
                print("User %d insert %s!" % (item['user_id'], record_id))
            else:
                print("User %d exist!" % item['user_id'])

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
