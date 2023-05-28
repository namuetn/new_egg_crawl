# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import json


class NeweggCrawlerItem(scrapy.Item):
    itemId = scrapy.Field()
    title = scrapy.Field()
    branding = scrapy.Field()
    rating = scrapy.Field()
    ratingCount = scrapy.Field()
    price = scrapy.Field()
    shipping = scrapy.Field()
    imgUrl = scrapy.Field()
    productsUrl = scrapy.Field()
    detailUrl = scrapy.Field()
    detailProduct = scrapy.Field(serializer=json.dumps)
