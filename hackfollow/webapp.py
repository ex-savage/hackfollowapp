from aiohttp import web
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from hackfollow import settings
from hackfollow.model import LinkModel, db
from hackfollow.model.magic.helpers import ThreadSwitcherWithDB, db_in_thread


class ValidateError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


async def validate_params(order, limit, offset):
    if order:
        if order.startswith('-'):
            order = order[1:]
        if order.endswith('id'):
            order = LinkModel.replace_id()
        try:
            getattr(LinkModel, order)
        except AttributeError:
            raise ValidateError('Wrong parameter for order!')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            raise ValidateError('Limit should be integer!')
        if limit > settings.max_limit:
            raise ValidateError(f'Max limit {settings.max_limit} allowed!')
    if offset:
        try:
            int(offset)
        except ValueError:
            raise ValidateError('Offset should be integer!')


@ThreadSwitcherWithDB.optimized
async def list_posts(request: Request):
    order = request.rel_url.query.get('order')
    limit = request.rel_url.query.get('limit')
    offset = request.rel_url.query.get('offset')
    try:
        await validate_params(order, limit, offset)
    except ValidateError as exc:
        return json_response(data={'error': exc.message}, status=web.HTTPBadRequest.status_code)
    async with db_in_thread():
        query = db.query(LinkModel)
        if order:
            query = LinkModel.sort_query(query, [order])
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

    result = [item.to_dict() for item in query]
    return json_response(data={'items': result, 'total': len(result)})


def setup_routes(app: Application):
    app.add_routes([
        web.get('/posts', list_posts),
    ])
