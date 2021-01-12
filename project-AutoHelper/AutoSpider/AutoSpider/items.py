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

    pass
