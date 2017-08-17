# -*- coding:utf-8 -*-
import re

import bs4
import requests
from bs4 import BeautifulSoup


def get_book_info(book_url):
    r = requests.get(book_url)
    book = {}
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')

        book['title'] = ''
        if soup.find(id='wrapper'):
            book['title'] = bs4_get_text(soup.find(id='wrapper').h1.span)

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

        book['catalog'] = ''
        if relate_info.find(id="dir_" + subject_id + "_full"):
            book['catalog'] = bs4_get_text(relate_info.find(id="dir_" + subject_id + "_full"))

        book['rating_score'] = 0
        if soup.find(class_=re.compile('ll rating_num')):
            book['rating_score'] = bs4_get_text(soup.find(class_=re.compile('ll rating_num')))

        book['rating_people'] = 0
        if soup.find(class_=re.compile('rating_people')):
            rating_people = bs4_get_text(soup.find(class_=re.compile('rating_people')))
            pos = rating_people.find(u'人评价')
            if pos:
                book['rating_people'] = rating_people[:pos]

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


def get_search_book_list(keyword):
    douban_url = "https://book.douban.com/subject_search?search_text=" + keyword
    r = requests.get(douban_url)
    book_list = []
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        item_list = soup.find_all(class_='subject-item')
        print item_list
        for item in item_list:
            book = {}
            book['pic'] = item.img.attrs.get('src')
            onclick_attr = item.a.attrs.get("onclick")
            subject_id = onclick_attr[onclick_attr.find("subject_id:") + 12:onclick_attr.find(",from") - 1]
            book['subject_id'] = subject_id
            book_url = item.h2.a.attrs.get('href')
            if book_url.find('book.douban.com/subject/') == -1:
                break
            book['url'] = book_url
            book_name = ''
            name_list = item.h2.a.contents
            for x in name_list:
                book_name = book_name + repr(x).strip()
            book['name'] = item.h2.a.get_text().strip().replace(' ', '').replace("\n", "")
            book['pub'] = item.find(class_='pub').get_text().strip()
            if item.find(class_='rating_nums') is not None:
                book['rating_nums'] = item.find(class_='rating_nums').get_text().strip() + u'分'
            else:
                book['rating_nums'] = ''
            if item.find(class_='pl') is not None:
                book['rating_peoples'] = item.find(class_='pl').get_text().strip()
            else:
                book['rating_peoples'] = ''
            book_list.append(book)
    return book_list
