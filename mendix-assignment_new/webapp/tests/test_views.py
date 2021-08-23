import pytest
from aiohttp.test_utils import make_mocked_request

from webapp.webapp.views.default import hello, initiate

pytestmark = pytest.mark.asyncio


async def test_hello():
    req = make_mocked_request("GET", "/hello")
    resp = await hello(req)
    assert resp.status == 200


async def test_initiate_validation():
    request = make_mocked_request(
        "POST",
        "/initiate",
        data={
            'start_date': '2021-08-10',
            'end_date': '2021-08-11',
        }
    )
    resp = await initiate(request)
    assert resp.status == 200
