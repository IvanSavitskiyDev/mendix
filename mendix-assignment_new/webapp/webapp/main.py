import logging
from aiohttp import web

from webapp import routes


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def create_app():
    """Return a aiohttp web applicastion."""
    app = web.Application()

    logger.info("Setting up application routes")
    routes.setup_routes(app)
    return app
