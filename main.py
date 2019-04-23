#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import logging
import json
import os
import sys
import random
import time
import traceback

from lxml import etree
import requests

import config
from init_logger import init_logger
from mail import send_mail, add_error_log_mail_handler

logger = logging.getLogger(__name__)

system = config.mail['subject_prefix']
locations = config.locations
receive_mail_addresses = config.mail['receivers']

rooms_filepath = '/app/danke_rooms.json'


class DankeRentSpider(object):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.86 Safari/537.36',
    }

    search_url = 'https://www.danke.com/room/sz'

    def get_room_url_title_list(self, query):
        params = dict(search=1, search_text=query)
        response = requests.get(
            url=self.search_url, params=params,
            headers=self.default_headers
        )
        if response.status_code != 200:
            logger.error(
                '查询房子接口失败 url: {} rsp: {}'.format(self.search_url, response)
            )

        root = etree.HTML(response.text)
        xpath = '//div[@class="r_ls_box"]//a[@title]'
        link_nodes = root.xpath(xpath)
        for node in link_nodes:
            yield node.get('href'), node.get('title')

    def get_room_desc_div(self, url):
        response = requests.get(url=url)
        if response.status_code != 200:
            logger.error('获取房子接口失败, url: {} rsp: {}'.format(url, response))

        root = etree.HTML(response.content)
        xpath = '//div[@class="room-detail"]'
        try:
            div_element = root.xpath(xpath)[0]
            return etree.tostring(div_element).decode()
        except:
            logger.error('获取房子接口失败, url: {} rsp: {} {}'.format(url, response, traceback.format_exc()))


class Diff(object):

    def __init__(self, new_dicts):
        self.filepath = rooms_filepath
        self.old_dicts = self._load_old_items_from_disk()
        self.new_dicts = new_dicts

        self._save_items_to_disk({**self.old_dicts, **self.new_dicts})

    def get_added_items(self):
        # 第一次创建旧文件不提醒
        if not self.old_dicts:
            return
        old_urls = list(set(self.old_dicts.keys()))
        added_urls = []
        for url, title in self.new_dicts.items():
            # 根据字符串相似度来选出新帖子
            if not difflib.get_close_matches(url, old_urls + added_urls, cutoff=0.99):
                added_urls.append(url)
                yield url, title

    def _load_old_items_from_disk(self):
        if not os.path.isfile(self.filepath):
            return {}
        return json.load(open(self.filepath, encoding='utf8'))

    def _save_items_to_disk(self, new_dicts):
        f = open(self.filepath, 'w', encoding='utf8')
        f.write(json.dumps(new_dicts, indent=4, ensure_ascii=False))
        f.flush()
        f.close()


def get_new_rooms():
    for location in locations:
        room_list = DankeRentSpider().get_room_url_title_list(location)
        rooms_dict = dict(room_list)
        added_rooms = Diff(rooms_dict).get_added_items()
        for url, title in added_rooms:
            yield url, title
        time.sleep(random.randint(10, 30))


def send_room_mail(room_url, room_title):
    room_desc_div = DankeRentSpider().get_room_desc_div(room_url)
    content = '''
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    </head>
    <body>
        <a href="{url}">原文链接</a>
        {div}
    </body>
</html>
'''.format(url=room_url, div=room_desc_div)

    send_mail(
        to=receive_mail_addresses,
        subject=room_title,
        content=content,
        type='html',
        system=system
    )


def monitor_rooms():
    while True:
        new_rooms = get_new_rooms()
        for url, title in new_rooms:
            send_room_mail(url, title)
            time.sleep(5)
        time.sleep(60 * random.randint(10, 30))


if __name__ == '__main__':

    add_error_log_mail_handler(logger, system)

    try:
        monitor_rooms()
    except:
        logger.error('程序异常终止', traceback.format_exc())
