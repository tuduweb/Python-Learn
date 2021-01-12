import scrapy
import json

class LearnerhubSpider(scrapy.Spider):
    name = 'learnerhub'
    allowed_domains = ['learnerhub.net']
    #start_urls = ['https://learnerhub.net/']


    #https://api.learnerhub.net/v1/products/704/count
    #https://api.learnerhub.net/v1/products/704/pull_quests?select_type=unsolved&page=1

    def start_requests(self):
        return [scrapy.Request('https://api.learnerhub.net/v1/products/704/pull_quests?select_type=unsolved&page=1', meta={'cookiejar': 1, 'step' : 1}, callback=self.parse_page)]
        pass

    def parse_page(self, response):
        rs = json.loads(response.text)
        print(rs)

        if rs.get('kaminari', {}).get('next_page') is not None:
            page = rs.get('kaminari', {}).get('next_page')
            if page > 1:
                yield scrapy.Request('https://api.learnerhub.net/v1/products/704/pull_quests?select_type=unsolved&page=' + str(page), callback=self.parse_page)

        pass

    def parse(self, response):
        #rs = json.loads(response.text)
        #print(rs)

        print(response.text)

        pass
