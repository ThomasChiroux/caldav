"""aiocaldav unittests. Test Free busy."""
import datetime
import uuid

from dateutil.tz import tzutc
import pytest
import pytz
import vobject

from aiocaldav.davclient import DAVClient
from aiocaldav.lib import error
from aiocaldav.objects import (Calendar, Event, FreeBusy)

from .fixtures import (backend, event_fixtures, event1, event2, event3)


@pytest.fixture(scope="module")
def eventfb_2_adjacent(request):
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:43b08621-af35-46a4-a6a6-7a40b4583ab2
DTSTAMP:20070712T182146Z
DTSTART:20070715T040000Z
DTEND:20070715T180000Z
SUMMARY:test adjacent event
END:VEVENT
END:VCALENDAR"""


@pytest.fixture(scope="module")
def eventfb_2_nonadjacent(request):
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:43b08621-af35-46a4-a6a6-7a40b4583ab2
DTSTAMP:20070712T182146Z
DTSTART:20070715T060000Z
DTEND:20070715T190000Z
SUMMARY:test adjacent event
END:VEVENT
END:VCALENDAR"""


@pytest.fixture(scope="module")
def event3_opaque(request):
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:19970901T130000Z-123403@example.com
DTSTAMP:19970901T130000Z
DTSTART;VALUE=DATE:19971102
SUMMARY:Our Blissful Anniversary
TRANSP:OPAQUE
CLASS:CONFIDENTIAL
CATEGORIES:ANNIVERSARY,PERSONAL,SPECIAL OCCASION
RRULE:FREQ=YEARLY
END:VEVENT
END:VCALENDAR"""


@pytest.mark.asyncio
async def test_free_busy_naive_1(backend, event2):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        # pytest.skip()
        pass
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event2)
    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(2007, 7, 13, 17, 00, 00),
                                          datetime.datetime(2007, 7, 15, 17, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_naive_2(backend, event1, event2, eventfb_2_adjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_adjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(2007, 7, 13, 17, 00, 00),
                                          datetime.datetime(2007, 7, 15, 17, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 2

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    assert freebusy.instance.vfreebusy.freebusy_list[1].value[0] == (
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 18, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_naive_3(backend, event1, event2, eventfb_2_adjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_adjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(2007, 7, 13, 17, 00, 00),
                                          datetime.datetime(2007, 7, 15, 3, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_naive_4(backend, event1, event2, eventfb_2_nonadjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_nonadjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(2007, 7, 13, 17, 00, 00),
                                          datetime.datetime(2007, 7, 15, 17, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 2

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    assert freebusy.instance.vfreebusy.freebusy_list[1].value[0] == (
        datetime.datetime(2007, 7, 15, 6, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 19, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_naive_5(backend, event1, event2, eventfb_2_nonadjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_nonadjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(2007, 7, 13, 17, 00, 00),
                                          datetime.datetime(2007, 7, 15, 3, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_naive_6(backend, event3):
    """Test free busy of a recurring transparent event."""
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event3)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(1997, 11, 1, 17, 00, 00),
                                          datetime.datetime(1997, 11, 3, 19, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert hasattr(freebusy.instance.vfreebusy, 'freebusy') is False

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_naive_7(backend, event3_opaque):
    """Test free busy of a recurring opaque event."""
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event3_opaque)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(datetime.datetime(2007, 11, 1, 17, 00, 00),
                                          datetime.datetime(2007, 11, 3, 19, 00, 00))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert hasattr(freebusy.instance.vfreebusy, 'freebusy') is True

    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 11, 2, 0, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 11, 3, 0, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_1(backend, event2):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        # pytest.skip()
        pass
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event2)
    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(2007, 7, 13, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2007, 7, 15, 17, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_2(backend, event1, event2, eventfb_2_adjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_adjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(2007, 7, 13, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2007, 7, 15, 17, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 2

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    assert freebusy.instance.vfreebusy.freebusy_list[1].value[0] == (
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 18, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_3(backend, event1, event2, eventfb_2_adjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_adjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(2007, 7, 13, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2007, 7, 15, 3, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_4(backend, event1, event2, eventfb_2_nonadjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_nonadjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(2007, 7, 13, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2007, 7, 15, 17, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 2

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    assert freebusy.instance.vfreebusy.freebusy_list[1].value[0] == (
        datetime.datetime(2007, 7, 15, 6, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 19, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_5(backend, event1, event2, eventfb_2_nonadjacent):
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event1)
    await cal.add_event(event2)
    await cal.add_event(eventfb_2_nonadjacent)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(2007, 7, 13, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2007, 7, 15, 3, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 7, 14, 17, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 7, 15, 4, 0, tzinfo=pytz.utc))

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_6(backend, event3):
    """Test free busy of a recurring transparent event."""
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event3)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(1997, 11, 1, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(1997, 11, 3, 19, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert hasattr(freebusy.instance.vfreebusy, 'freebusy') is False

    await principal.prune()


@pytest.mark.asyncio
async def test_free_busy_utc_7(backend, event3_opaque):
    """Test free busy of a recurring opaque event."""
    if backend.get("name") == "radicale":
        # radicale does not support freebusy yet
        pytest.skip()
    uri = backend.get('uri')
    # instead of a fixed login we generate a random one in order to start with an
    # empty principal.
    login = backend.get('login', uuid.uuid4().hex)
    password = backend.get('password', uuid.uuid4().hex)
    caldav = DAVClient(uri, username=login,
                       password=password, ssl_verify_cert=False)
    principal = await caldav.principal()

    cal_id = uuid.uuid4().hex
    cal = await principal.make_calendar(name="Yep", cal_id=cal_id)
    assert cal.url == uri + login + "/" + cal_id + '/'
    events = await cal.events()
    assert len(events) == 0

    await cal.add_event(event3_opaque)

    # Lets try a freebusy request as well
    freebusy = await cal.freebusy_request(
        datetime.datetime(2007, 11, 1, 17, 00, 00,
                          tzinfo=datetime.timezone.utc),
        datetime.datetime(2007, 11, 3, 19, 00, 00,
                          tzinfo=datetime.timezone.utc))

    assert isinstance(freebusy, FreeBusy)
    assert freebusy.instance.vfreebusy
    assert hasattr(freebusy.instance.vfreebusy, 'freebusy') is True

    assert len(freebusy.instance.vfreebusy.freebusy_list) == 1

    assert freebusy.instance.vfreebusy.freebusy_list[0].value[0] == (
        datetime.datetime(2007, 11, 2, 0, 0, tzinfo=pytz.utc),
        datetime.datetime(2007, 11, 3, 0, 0, tzinfo=pytz.utc))

    await principal.prune()
