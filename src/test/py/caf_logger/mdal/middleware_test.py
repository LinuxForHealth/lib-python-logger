from caf_logger.mdal import middleware
import asynctest
import importlib
import uuid
from aiohttp import web, test_utils
from caf_logger.mdal import constants
import json
import caf_logger.logger


class TestMiddleware(asynctest.TestCase):
    def setUp(self):
        importlib.reload(caf_logger.logger)

    async def test_response(self):
        async def func(request):
            return web.Response(text="successful")

        app = web.Application(middlewares=[middleware.read_write_mdal])
        app.router.add_route('GET', '/', func)
        uuid_str = str(uuid.uuid4())
        headers = {constants.CORRID_HEADER_NAME: constants.UUID_CORRID_LABEL + uuid_str}
        req = test_utils.make_mocked_request('GET', '/', headers)

        resp = await middleware.read_write_mdal(req,func)
        print(constants.UUID_CORRID_LABEL+uuid_str)
        print(json.loads(resp.headers[constants.CORRID_HEADER_NAME])[0])
        assert constants.UUID_CORRID_LABEL+uuid_str == json.loads(resp.headers[constants.CORRID_HEADER_NAME])[0]

