import scrapy
import json
from AutoSpider.items import AutospiderItem


class LearnerhubSpider(scrapy.Spider):
    name = 'learnerhub'
    allowed_domains = ['learnerhub.net']
    # start_urls = ['https://learnerhub.net/']
    current_num = 0
    user_data = []

    # https://api.learnerhub.net/v1/products/704/count
    # https://api.learnerhub.net/v1/products/704/pull_quests?select_type=unsolved&page=1

    def start_requests(self):
        return [scrapy.Request('https://api.learnerhub.net/v1/products/704/pull_quests?select_type=unsolved&page=1',
                               meta={'cookiejar': 1, 'step': 1}, callback=self.parse_page)]
        pass

    def parse_page(self, response):
        rs = json.loads(response.text)
        # print(rs.get('data'))

        data = rs.get('data')

        if data is not None:
            self.user_data.append(data)
            for item in data:
                data_item = AutospiderItem()
                data_item['title'] = item.get('title')
                data_item['description'] = item.get('description')
                data_item['owner'] = item.get('owner')
                data_item['attachments'] = item.get('pull_quest_items')
                data_item['json_data'] = item
                data_item['updated_time'] = item.get('updated_at')
                #print(data_item['updated_time'])
                data_item['file_urls'] = []
                data_item['post_id'] = item.get('id')
                if data_item['attachments'] is not None:
                    self.current_num += 1
                # print('')
                if self.current_num == 1:  # bypass
                    yield data_item
            pass

        # print(self.user_data)

        if rs.get('kaminari', {}).get('next_page') is not None:
            page = rs.get('kaminari', {}).get('next_page')
            if False and page > 1:
                yield scrapy.Request(
                    'https://api.learnerhub.net/v1/products/704/pull_quests?select_type=unsolved&page=' + str(page),
                    callback=self.parse_page)
                pass
        pass

    # 爬取回复信息
    def parse_comments(self, response):
        pass

    def parse(self, response):
        # rs = json.loads(response.text)
        # print(rs)

        print(response.text)

        pass
