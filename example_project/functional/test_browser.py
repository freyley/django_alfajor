# Copyright Action Without Borders, Inc., the Alfajor authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'alfajor' and is distributed under the BSD license.
# See LICENSE for more details.

import time

from nose.tools import raises, set_trace

from . import browser


def test_simple():
    browser.open('/')

    if 'status' in browser.capabilities:
        assert browser.status_code == 200
        assert browser.status == '200 OK'
    if 'headers' in browser.capabilities:
        assert 'text/html' in browser.headers['Content-Type']
    assert not browser.cookies


def test_reset():
    # TODO: flesh this out when cookie querying is working and has
    # test coverage.  until then, just verify that the method doesn't
    # explode.
    browser.open('/')
    browser.reset()


def test_user_agent():
    browser.open('/')
    ua = browser.user_agent
    assert ua['browser'] != 'unknown'


from foo.models import Foo
def test_foo():
    Foo.objects.all().delete()
    browser.open('/foo')
    set_trace()
    assert len(browser.document['#foos li']) == 0
    Foo.objects.create(dumbness=True)
    browser.open('/foo')
    assert len(browser.document['#foos li']) == 1
