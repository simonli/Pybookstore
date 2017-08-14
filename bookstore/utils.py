# -*- coding:utf-8 -*-
import hashlib
import os
import random
import re
import string
import uuid
from datetime import datetime

import bs4
import requests
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup

current_dir = os.path.abspath(os.path.dirname(__file__))


def generate_verification_code():
    codenum = 4
    source = list(string.letters)
    for index in range(0, 10):
        source.append(str(index))
    code = ''.join(random.sample(source, 4))

    # 设置图片大小
    width = 80
    height = 40
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 选择字体
    fontfile = os.path.join(current_dir, 'static/consola.ttf')
    font = ImageFont.truetype(fontfile, 24)
    draw = ImageDraw.Draw(image)

    for x in range(width):
        for y in range(height):
            colorRandom1 = (random.randint(255, 255), random.randint(255, 255), random.randint(255, 255))
            draw.point((x, y), fill=colorRandom1)

        for t in range(codenum):
            colorRandom2 = (random.randint(1, 80), random.randint(1, 80), random.randint(1, 80))
            draw.text((16 * t + 10, 10), code[t], font=font, fill=colorRandom2)
    image_d = ImageDraw.Draw(image)
    for i in range(5):
        colorRandom3 = (random.randint(1, 80), random.randint(1, 80), random.randint(1, 80))
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        image_d.line([begin, end], fill=colorRandom3)

    return code, image


def unique_id():
    return str(uuid.uuid4())


def get_book_info(book_url):
    r = requests.get(book_url)
    book = {}
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')

        book['name'] = ''
        if soup.find(id='wrapper'):
            book['name'] = bs4_get_text(soup.find(id='wrapper').h1.span)

        book['logo'] = ''
        if soup.find(class_='nbg'):
            book['logo'] = soup.find(class_='nbg').img.attrs.get('src')

        node = soup.find(id='info')

        book['author'] = ''
        if node.a:
            book['author'] = bs4_get_text(node.a)

        book['publisher'] = ''
        if node.find(text=re.compile(u'出版社')):
            book['publisher'] = node.find(text=re.compile(u'出版社')).next_element

        book['translator'] = ''
        if node.find(text=re.compile(u'译者')):
            book['translator'] = book['translator'] = bs4_get_text(node.find(text=re.compile(u'译者')).parent.parent.a)

        book['isbn'] = ''
        if node.find(text=re.compile(u'ISBN')):
            book['isbn'] = node.find(text=re.compile(u'ISBN')).next_element

        subject_id = book_url[book_url.find('subject') + 8:book_url.rfind('/')]
        book['subject_id'] = subject_id

        relate_info = soup.find(class_='related_info')

        book['book_intro'] = ''
        if relate_info.find(class_='all hidden'):
            book['book_intro'] = bs4_get_text(relate_info.find(class_='all hidden').find(class_='intro'))

        book['author_intro'] = ''
        if relate_info.find(text=re.compile(u'作者简介')):
            book['author_intro'] = bs4_get_text(
                relate_info.find(text=re.compile(u'作者简介')).parent.parent.next_sibling.next_sibling.find(
                    class_='intro'))

        book['book_catalog'] = ''
        if relate_info.find(id="dir_" + subject_id + "_full"):
            book['book_catalog'] = bs4_get_text(relate_info.find(id="dir_" + subject_id + "_full"))

        book['rating_score'] = ''
        if soup.find(class_=re.compile('ll rating_num')):
            book['rating_score'] = bs4_get_text(soup.find(class_=re.compile('ll rating_num')))

        book['rating_people'] = ''
        if soup.find(class_=re.compile('rating_people')):
            book['rating_people'] = bs4_get_text(soup.find(class_=re.compile('rating_people')))

        tag_list = []
        tag_node_list = soup.find_all(class_=re.compile('tag'))
        for x in tag_node_list:
            xx = bs4_get_text(x)
            xx_list = re.split('\\s+', xx)
            for x3 in xx_list:
                tag_list.append(x3)
        book['tags'] = tag_list
    return book


def bs4_get_text(obj):
    if obj is not None:
        if type(obj) is bs4.element.Tag:
            return obj.get_text()
    else:
        return ''


def get_md5sum(filepath):
    md5sum = ''
    if os.path.exists(filepath):
        rb = open(filepath, 'rb')
        rb_md5 = hashlib.md5()
        rb_md5.update(rb.read())
        md5sum = rb_md5.hexdigest()
    return md5sum


def get_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    else:
        ext = os.path.splitext(filename)[1]
        if ext.startswith('.'):
            ext = ext[1:].lower()
        return ext


def get_namebasetime():
    return '%s%s' % (datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'), datetime.now().microsecond)


if __name__ == "__main__":
    im = generate_verification_code()
    im.show()
