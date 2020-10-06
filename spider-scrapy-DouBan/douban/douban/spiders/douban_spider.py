import scrapy
from douban.items import DoubanItem,CommentItem

import re

class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250']

    comment_parge = 1

    def parse(self, response):
        movie_list = response.xpath("//div[@class='article']//ol[@class='grid_view']/li")
        for i_item in movie_list:
            douban_item = DoubanItem()
            douban_item['serial_number'] = i_item.xpath(".//div[@class='item']//em/text()").extract_first()
            douban_item['movie_name'] = i_item.xpath(".//div[@class='info']/div[@class='hd']/a/span[1]/text()").extract_first()
            content = i_item.xpath(".//div[@class='info']//div[@class='bd']/p[1]/text()").extract()
            for i_content in content:
                content_s = "".join(i_content.split())
                douban_item['introduce'] = content_s
            douban_item['star'] =  float(i_item.xpath(".//span[@class='rating_num']/text()").extract_first())
            douban_item['evaluate'] = int(re.sub("\D", "", i_item.xpath(".//div[@class='star']//span[4]/text()").extract_first()))
            douban_item['describe'] = i_item.xpath(".//p[@class='quote']//span/text()").extract_first()
            
            movie_href = i_item.xpath(".//div[@class='info']/div[@class='hd']/a/@href").extract_first()
            douban_item['movie_id'] = int(movie_href.split('/')[-2])

            yield douban_item

            # 在for循环中提交详情爬取
            yield scrapy.Request("https://movie.douban.com/subject/" + str(douban_item['movie_id']) + "/reviews", callback=self.parse_comment, meta={'movie_id': douban_item['movie_id']})

        next_link = response.xpath("//span[@class='next']/link/@href").extract()
        if next_link:
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/top250"+next_link,callback=self.parse)

    #爬取评论
    def parse_comment(self, response):
        comment_list = response.xpath("//div[@class='review-list  ']/div[@data-cid]")
        for i_item in comment_list:
            
            comment_item = CommentItem()

            comment_item['movie_id'] = response.meta['movie_id']
            comment_item['comment_id'] = int(i_item.xpath("./@data-cid").extract_first())
            
            yield scrapy.Request("https://movie.douban.com/review/" + str(comment_item['comment_id']) + "/", callback=self.parse_comment_detail, meta={'item': comment_item})
            #yield comment_item
        next_link = response.xpath("//span[@class='next']/link/@href").extract()
        if next_link and self.comment_parge < 3: #暂时只爬少量
            self.comment_parge += 1
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/subject/" + str(comment_item['movie_id']) + "/reviews" + next_link, callback=self.parse_comment, meta={'movie_id': comment_item['movie_id']})

    #爬取详情
    def parse_comment_detail(self, response):
        comment_item = response.meta['item']
        comment_item['user_key'] = response.xpath("//div[@class='main']/a/@href").extract_first().split('/')[-2]
        comment_item['title'] = response.xpath("//span[@property='v:summary']/text()").extract_first()
        #comment_item['content'] = response.xpath("//div[contains(@class, 'review-content')]/text()").extract()
        #comment_item['content'] = response.xpath("//div[@id='link-report']/text()").extract()
        content_node = response.xpath("//div[@class='review-content clearfix']")
        comment_item['content'] = content_node.xpath("string(.)").extract_first().replace('\r', "").replace('\n', "")
        
        useful_node = response.xpath("//div[@class='main-panel-useful']")
        comment_item['count_useful'] = [int(s) for s in useful_node.xpath("//button[contains(@class, 'useful_count')]/text()").extract_first().split() if s.isdigit()][0]
        comment_item['count_useless'] = [int(s) for s in useful_node.xpath("//button[contains(@class, 'useless_count')]/text()").extract_first().split() if s.isdigit()][0]

        comment_item['last_time'] = response.xpath("//span[@class='main-meta']/text()").extract_first()
        yield comment_item
