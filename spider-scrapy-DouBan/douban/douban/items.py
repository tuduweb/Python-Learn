# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    serial_number = scrapy.Field()
    movie_name = scrapy.Field()
    introduce = scrapy.Field()
    star = scrapy.Field()
    evaluate = scrapy.Field()
    describe = scrapy.Field()

    movie_id = scrapy.Field()

class CommentItem(scrapy.Item):
    _id = scrapy.Field()

    movie_id = scrapy.Field()
    comment_id = scrapy.Field()
    user_key = scrapy.Field()

    title = scrapy.Field()
    content = scrapy.Field()

    count_useful = scrapy.Field()
    count_useless = scrapy.Field()
    last_time = scrapy.Field()