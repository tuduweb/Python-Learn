# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AutospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    owner = scrapy.Field()
    attachments = scrapy.Field()
    file_urls = scrapy.Field()
    json_data = scrapy.Field()
    updated_time = scrapy.Field()
    post_id = scrapy.Field()
    pass


class TopicItem(scrapy.Item):
    product_id = scrapy.Field()
    topic_id = scrapy.Field()

    title = scrapy.Field()
    content = scrapy.Field()
    owner_id = scrapy.Field()
    created_at = scrapy.Field()


class CommentItem(scrapy.Item):
    topic_id = scrapy.Field()
    parent_id = scrapy.Field()
    comment_id = scrapy.Field()

    content = scrapy.Field()
    owner_id = scrapy.Field()
    created_at = scrapy.Field()

    receiver = scrapy.Field()
