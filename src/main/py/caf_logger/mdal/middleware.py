from caf_logger.mdal import corrid_store
from caf_logger.mdal import constants
import caf_logger.logger as caflogger
from caf_logger import logging_codes
from aiohttp import web
import json

logger = caflogger.get_logger("caf_logger.mdal")

@web.middleware
async def read_write_mdal(request, handler):

    if request.headers.get(constants.CORRID_HEADER_NAME) is None:
        logger.info(logging_codes.WHI_CAF_MDAL_NO_CORRID)
        corrid_store.init_headers()
    else:
        corrid_store.set_headers([request.headers[constants.CORRID_HEADER_NAME]])

    response = await handler(request)

    response.headers[constants.CORRID_HEADER_NAME] = json.dumps(corrid_store.get_headers())

    return response
