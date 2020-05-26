import pytest

from hackfollow import settings
from hackfollow.model import Link
from hackfollow.watcher import save_to_db


@pytest.mark.asyncio
async def test_empty(client):
    resp = await client.get('/posts')
    json_resp = await resp.json()
    assert json_resp == {'items': [], 'total': 0}
    assert resp.status == 200


@pytest.mark.asyncio
async def test_posts_api(client):
    post = Link('test', 'https://aaa.com')
    posts = [post]
    await save_to_db(posts)
    resp = await client.get('/posts')
    json_resp = await resp.json()
    assert resp.status == 200
    assert json_resp['total'] == 1
    items = json_resp['items']
    assert items[0]['url'] == post.url
    assert items[0]['title'] == post.title

    post2 = Link('test2', 'https://bbb.com')
    posts.append(post2)
    await save_to_db(posts)
    resp = await client.get('/posts')
    json_resp = await resp.json()
    assert resp.status == 200
    assert json_resp['total'] == 2
    items = json_resp['items']
    assert items[1]['url'] == post2.url
    assert items[1]['title'] == post2.title

    resp = await client.get('/posts?order=id')
    json_resp = await resp.json()
    assert resp.status == 200
    items = json_resp['items']
    assert items[0]['title'] == post.title

    resp = await client.get('/posts?order=-id')
    json_resp = await resp.json()
    assert resp.status == 200
    items = json_resp['items']
    assert items[0]['title'] == post2.title

    resp = await client.get('/posts?order=-url')
    json_resp = await resp.json()
    assert resp.status == 200
    items = json_resp['items']
    assert items[0]['url'] == post2.url

    resp = await client.get('/posts?order=-created')
    json_resp = await resp.json()
    assert resp.status == 200
    items = json_resp['items']
    assert items[0]['title'] == post2.title

    resp = await client.get('/posts?order=aaa')
    assert resp.status == 400
    json_resp = await resp.json()
    assert 'error' in json_resp

    resp = await client.get('/posts?offset=1')
    json_resp = await resp.json()
    assert json_resp['total'] == 1

    resp = await client.get('/posts?offset=aaa')
    assert resp.status == 400
    json_resp = await resp.json()
    assert 'error' in json_resp

    resp = await client.get(f'/posts?limit={settings.max_limit + 1}')
    assert resp.status == 400
    json_resp = await resp.json()
    assert 'error' in json_resp
