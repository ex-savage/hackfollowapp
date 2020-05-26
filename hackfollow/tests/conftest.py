import pytest
from aiohttp import web


def pytest_configure(config):
    from hackfollow import settings
    settings.test = True


@pytest.yield_fixture(scope='session')
def db():
    from hackfollow import model
    model.db.create_all()
    yield
    model.db.drop_all()


@pytest.fixture
def app(db):
    from hackfollow.webapp import setup_routes
    app = web.Application()
    setup_routes(app)
    yield app


@pytest.fixture
async def client(app, aiohttp_client, loop):
    yield await aiohttp_client(app)
