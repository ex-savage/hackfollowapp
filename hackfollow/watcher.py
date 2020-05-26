from typing import List

import aiohttp
import lxml.html
from loguru import logger

from hackfollow.model import Link, LinkModel, db
from hackfollow.model.magic.helpers import ThreadSwitcherWithDB, db_in_thread
from hackfollow.settings import HN_URL


async def hn_request(session: aiohttp.ClientSession):
    try:
        response = await session.get(HN_URL)
    except Exception:
        logger.exception('Error during hn request')
        return
    return await response.text()


async def parse_items(data):
    doc = lxml.html.fromstring(data)
    links = doc.xpath('.//tr[@class="athing"]//td[@class="title"]/a')
    links = [Link(link.text, link.get('href')) for link in links]
    return links


@ThreadSwitcherWithDB.optimized
async def save_to_db(links: List[Link]):
    new_items = 0
    async with db_in_thread():
        for link in links:
            item, created = LinkModel.create(link)
            if created:
                new_items += 1
            db.add(item)
        db.commit()
    logger.info(f'There are {new_items} item(s)')


async def check(session):
    data = await hn_request(session)
    if not data:
        return
    try:
        links = await parse_items(data)
    except Exception:
        logger.exception('Error during parsing the page')
        return
    await save_to_db(links)
