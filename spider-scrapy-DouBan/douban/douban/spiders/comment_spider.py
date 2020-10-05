import scrapy
from douban.items import CommentItem
from douban.items import DoubanItem

class GoCommentSpider(scrapy.Spider):
    name = 'comment'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/subject/1292052/reviews']
    page = 1

    #爬取详情
    def parse_detail(self, response):
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

    def parse(self, response):
        comment_list = response.xpath("//div[@class='review-list  ']/div[@data-cid]")
        for i_item in comment_list:
            
            comment_item = CommentItem()

            comment_item['comment_id'] = i_item.xpath("./@data-cid").extract_first()

            # douban_item = DoubanItem()
            # douban_item['serial_number'] = i_item.xpath(".//div[@class='item']//em/text()").extract_first()
            # douban_item['movie_name'] = i_item.xpath(".//div[@class='info']/div[@class='hd']/a/span[1]/text()").extract_first()
            # content = i_item.xpath(".//div[@class='info']//div[@class='bd']/p[1]/text()").extract()

            # comment_item['comment_id'] = i_item.xpath(".//div[@class='item']//em/text()").extract_first()

            # for i_content in content:
            #     content_s = "".join(i_content.split())
            #     douban_item['introduce'] = content_s
            # douban_item['star'] =  i_item.xpath(".//span[@class='rating_num']/text()").extract_first()
            # douban_item['evaluate'] = i_item.xpath(".//div[@class='star']//span[4]/text()").extract_first()
            # douban_item['describe'] = i_item.xpath(".//p[@class='quote']//span/text()").extract_first()
            
            yield scrapy.Request("https://movie.douban.com/review/" + comment_item['comment_id'] + "/", callback=self.parse_detail, meta={'item': comment_item})
            break
            #yield comment_item
        next_link = response.xpath("//span[@class='next']/link/@href").extract()
        if next_link and self.page < 1:
            self.page = self.page + 1
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/subject/1292052/reviews"+next_link,callback=self.parse)