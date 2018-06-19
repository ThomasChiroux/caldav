"""aiocaldav unittests. Test Events."""
import uuid

import pytest
import vobject

from aiocaldav.davclient import DAVClient
from aiocaldav.lib import error
from aiocaldav.objects import Calendar

from .fixtures import (backend, event1)


@pytest.mark.asyncio
async def test_create_event_1(backend, event1):
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = uuid.uuid4().hex
    password = uuid.uuid4().hex
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await  cal.add_event(event1)

    # c.events() should give a full list of events
    events = await cal.events()
    assert len(events) == 1

    # We should be able to access the calender through the URL
    cal2 = Calendar(client=caldav, url=cal.url)
    events2 = await cal2.events()
    assert len(events2) == 1
    assert events2[0].url == events[0].url


@pytest.mark.asyncio
async def test_create_event_2(backend, event1):
    """test with a VEVENT only calendar."""
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = uuid.uuid4().hex
    password = uuid.uuid4().hex
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id,
                                        supported_calendar_component_set=['VEVENT'])
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await  cal.add_event(event1)

    # c.events() should give a full list of events
    events = await cal.events()
    assert len(events) == 1

    # We should be able to access the calender through the URL
    cal2 = Calendar(client=caldav, url=cal.url)
    events2 = await cal2.events()
    assert len(events2) == 1
    assert events2[0].url == events[0].url


@pytest.mark.asyncio
async def test_create_delete_calendar_with_event(backend, event1):
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = uuid.uuid4().hex
    password = uuid.uuid4().hex
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await  cal.add_event(event1)

    # c.events() should give a full list of events
    events = await cal.events()
    assert len(events) == 1

    await cal.delete()

    # We should be able to access the calender through the URL
    cal2 = Calendar(client=caldav, url=cal.url)
    with pytest.raises(error.NotFoundError):
        await cal2.events()


@pytest.mark.asyncio
async def test_create_event_from_vobject(backend, event1):
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = uuid.uuid4().hex
    password = uuid.uuid4().hex
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)

    # add event from vobject data
    vevent1 = vobject.readOne(event1)
    await cal.add_event(vevent1)

    # c.events() should give a full list of events
    events = await cal.events()
    assert len(events) == 1

    # We should be able to access the calender through the URL
    cal2 = Calendar(client=caldav, url=cal.url)
    events2 = await cal2.events()
    assert len(events2) == 1
    assert events2[0].url == events[0].url


@pytest.mark.asyncio
async def test_create_event_in_journal_only_calendar(backend, event1):
    """This test does not pass with radicale backend: perhaps radicale accepts
    events even when the calendar should not support it ?"""
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = uuid.uuid4().hex
    password = uuid.uuid4().hex
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id,
                                        supported_calendar_component_set=['VJOURNAL'])
    if backend.get("name") == "radicale":
        await cal.add_event(event1)
    else:
        with pytest.raises(error.PutError):
            await cal.add_event(event1)


@pytest.mark.asyncio
async def test_create_event_in_todo_only_calendar(backend, event1):
    """This test does not pass with radicale backend: perhaps radicale accepts
    events even when the calendar should not support it ?"""
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = uuid.uuid4().hex
    password = uuid.uuid4().hex
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id,
                                        supported_calendar_component_set=['VTODO'])
    if backend.get("name") == "radicale":
        await cal.add_event(event1)
    else:
        with pytest.raises(error.PutError):
            await cal.add_event(event1)
