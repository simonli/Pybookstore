# -*- coding:utf-8 -*-
import hashlib
import os
import uuid
from datetime import datetime
from urlparse import urlparse, urljoin

import gvcode
from flask import request

current_dir = os.path.dirname(os.path.abspath(__file__))


def generate_verification_code():
    chars = 'ABCDEFGHKMNPQRSTUVWXY'
    font_file = os.path.join(os.path.dirname(current_dir), 'static/BRLNSR.TTF')
    image, code = gvcode.generate(chars=chars, font_file=font_file)
    return image, code


def unique_id():
    return str(uuid.uuid4())


def get_checksum(filepath):
    checksum = ''
    if os.path.exists(filepath):
        rb = open(filepath, 'rb')
        rb_md5 = hashlib.md5()
        rb_md5.update(rb.read())
        checksum = rb_md5.hexdigest()
    return checksum


def get_file_ext(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    else:
        ext = os.path.splitext(filename)[1]
        if ext.startswith('.'):
            ext = ext[1:].lower()
        return ext


def get_namebasetime():
    return '%s%s' % (datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'), datetime.now().microsecond)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


if __name__ == "__main__":
    im = generate_verification_code()
    im.show()
