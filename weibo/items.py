# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    collection = 'users'
    id = scrapy.Field()
    name = scrapy.Field()
    avatar = scrapy.Field()
    cover = scrapy.Field()
    gender = scrapy.Field()
    description = scrapy.Field()
    follows_count = scrapy.Field()
    fans_count = scrapy.Field()
    weibos_count = scrapy.Field()
    verified_reason = scrapy.Field()


class UserRelationItem(scrapy.Item):
    collection = 'users'
    id = scrapy.Field()
    follows = scrapy.Field()
    fans = scrapy.Field()


class WeiboItem(scrapy.Item):
    collection = 'weibos'
    id = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    reposts_count = scrapy.Field()
    source = scrapy.Field()
    text = scrapy.Field()
    thumbnail = scrapy.Field()
    user = scrapy.Field()
    created_at = scrapy.Field()
    crawled_at = scrapy.Field()
