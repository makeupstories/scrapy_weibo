# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import quote
from items import *


class MweiboSpider(scrapy.Spider):
    name = 'mweibo'
    allowed_domains = ['m.weibo.cn']
    basic_url = 'https://m.weibo.cn/api/container/getIndex?'
    user_url = basic_url + 'type=uid&value={uid}&containerid=100505{uid}'
    followers_url = basic_url \
                    + 'containerid=231051_-_followers_-_{uid}&' \
                    + 'luicode=10000011&' \
                    + 'lfid=107603{uid}&' \
                    + 'page={page}'
    fans_url = basic_url \
               + 'containerid=231051_-_fans_-_{uid}&' \
               + 'luicode=10000011&' \
               + 'lfid=107603{uid}&' \
               + 'since_id={page}'
    weibo_url = basic_url + 'type=uid&value={uid}&containerid=107603{uid}&page={page}'

    start_users = ['1826792401', '1717759773', '3217179555', '1742566624']

    def start_requests(self):
        for uid in self.start_users:
            yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user())

    def parse_user(self, response):
        '''
        解析用户信息
        :param response: Response对象
        '''
        # self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id': 'id',
                'name': 'screen_name',
                'avatar': 'avatar_hd',
                'cover': 'cover_image_phone',
                'gender': 'gender',
                'description': 'description',
                'follows_count': 'follow_count',
                'fans_count': 'followers_count',
                'weibos_count': 'statuses_count',
                'verified_reason': 'verified_reason'
            }
            for field, attr in field_map.items():  # 返回可遍历的(键, 值) 元组数组。
                user_item[field] = user_info.get(attr)
            yield user_item

            # 关注
            uid = user_info.get('id')
            yield scrapy.Request(self.followers_url.format(uid=uid, page=1), callback=self.parse_follows,
                                 meta={'page': 1, 'uid': uid})

            # 粉丝
            yield scrapy.Request(self.fans_url.format(uid=uid, page=1), callback=self.parse_fans,
                                 meta={'page': 1, 'uid': uid})

            # 微博
            yield scrapy.Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                                 meta={'page': 1, 'uid': uid})

    def parse_follows(self, response):
        '''
        解析用户关注
        :param response:
        :return:
        '''
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get('card_group'):
            # 解析用户
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

            # 关注列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')} for follow in
                       follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item

            # 下一页关注
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.followers_url.format(uid=uid, page=page), callback=self.parse_follows,
                                 meta={'page': page, 'uid': uid})

    def parse_fans(self, response):
        '''
        解析用户粉丝

        :return:
        '''
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get(
                'data').get('cards')[-1].get('card_group'):
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield scrapy.Request(self.fans_url.format(uid=uid), callback=self.parse_fans)

            # 粉丝列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')} for fan in fans]
            user_relation_item['id'] = uid
            user_relation_item['fans'] = fans
            user_relation_item['follows'] = []
            yield user_relation_item

            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.fans_url.format(uid=uid, page=page), callback=self.parse_fans,
                                 meta={'page': page, 'uid': uid})

    def parse_weibos(self, response):
        '''
        解析微博列表
        :param response:
        :return:
        '''
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id',
                        'attitudes_count': 'attitudes_count',
                        'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count',
                        'source': 'source',
                        'text': 'text',
                        'thumbnail': 'thumbnail_pic',
                        'created_at': 'created_at'
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item

            # 下一页
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                                 meta={'uid': uid, 'page': page})
