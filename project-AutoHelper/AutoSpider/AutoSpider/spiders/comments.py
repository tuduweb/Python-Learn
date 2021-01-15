import scrapy
import json
from AutoSpider.items import TopicItem
#from AutoSpider.AutoSpider.items import TopicItem
from AutoSpider.items import CommentItem
#from AutoSpider.AutoSpider.items import CommentItem


class CommentsSpider(scrapy.Spider):
    name = 'comments'
    allowed_domains = ['learnerhub.net']

    # start_urls = ['http://learnerhub.net/']

    def start_requests(self):
        return [scrapy.Request(
            'https://api.learnerhub.net/v1/products/681/issues?'
            'select_type=all&page=1&order_type=updated&order_action=desc',
            meta={'cookiejar': 1}, callback=self.parse_topic_list)]
        pass

    def parse_topic_list(self, response):
        rs = json.loads(response.text)
        # print(rs)

        for topic in rs.get('data'):
            topic_item = TopicItem()
            # 存储新的topic信息
            topic_id = topic.get('id')
            # 在topic中分发采集topic详细信息的任务(需要有comment才采集吧)
            topic_item['product_id'] = topic.get('product_id')
            topic_item['topic_id'] = topic.get('id')

            topic_item['title'] = topic.get('title')
            topic_item['content'] = topic.get('content')
            topic_item['owner_id'] = topic.get('owner').get('id')
            topic_item['created_at'] = topic.get('created_at')

            if topic_id > 0:
                yield scrapy.Request('https://api.learnerhub.net/v1/comments?'
                                     'commentable_type=Issue&commentable_id=%d' % topic_id,
                                     meta={'cookiejar': 1}, callback=self.parse_topic_detail)

                if topic.get('discuss_count', 0) > 0:
                    yield scrapy.Request('https://api.learnerhub.net/v1/comments?commentable_type=Issue'
                                         '&commentable_id=%d&page=1&per_number=10&role=discuss' % topic_id,
                                         meta={'cookiejar': 1, 'pid': topic.get('id')},
                                         callback=self.parse_comment_detail)

            # 如果有discuss_count那么代表在问题中带有问题的直接回复
            # https://api.learnerhub.net/v1/comments?commentable_type=Issue&commentable_id=9586&page=1&per_number=3&role=discuss

            pass

        pass

    def parse_topic_detail(self, response):
        rs = json.loads(response.text)
        # print(rs)

        # https://api.learnerhub.net/v1/comments/38007/children?page=1&per_number=3

        for comment in rs.get('data'):
            comment_item = CommentItem()
            comment_item['topic_id'] = comment.get('commentable_id')
            comment_item['parent_id'] = 0
            comment_item['comment_id'] = comment.get('id')

            comment_item['content'] = comment.get('content')
            comment_item['owner_id'] = comment.get('user').get('id')
            comment_item['created_at'] = comment.get('created_at')

            if comment.get('receiver') is not None:
                comment_item['receiver'] = comment.get('receiver').get('id')
            # children_count 是回复数量.. 根据id查找
            # id
            # https://api.learnerhub.net/v1/comments?commentable_type=Issue&commentable_id=9586&page=1&per_number=3&role=discuss
            comment_id = comment.get('id')
            if comment.get('children_count', 0) > 0 and comment_id > 0:
                yield scrapy.Request('https://api.learnerhub.net/v1/'
                                     'comments/%d/children?page=1&per_number=10' % comment_id,
                                     meta={'cookiejar': 1},
                                     callback=self.parse_comment_detail)

            # print(comment.get('content'))

        pass

    def parse_comment_detail(self, response):
        # father_id
        #parent_id = response.meta.get('pid')
        rs = json.loads(response.text)

        print(rs)

        for comment in rs.get('data'):
            comment_item = CommentItem()
            comment_item['topic_id'] = comment.get('commentable_id')
            comment_item['parent_id'] = comment.get('parent_id')
            comment_item['comment_id'] = comment.get('id')

            comment_item['content'] = comment.get('content')
            comment_item['owner_id'] = comment.get('user').get('id')
            comment_item['created_at'] = comment.get('created_at')

            if comment.get('receiver') is not None:
                comment_item['receiver'] = comment.get('receiver').get('id')

        pass

    def parse(self, response):
        pass
