## hackfollow

Simple app to grab news from https://news.ycombinator.com/

#### Run your own instance with docker
```shell script
cd docker
docker-compose build
docker-compose run -w /code/hackfollow/model web alembic upgrade head
docker-compose up -d
``` 

Manage configuration with [settings.py](hackfollow/settings.py)

#### API

Main endpoint GET `/posts`

Open `localhost:5555/posts` and enjoy

```
localhost:5555/posts?order=-created
localhost:5555/posts?order=-id
localhost:5555/posts?order=-title&limit=5
localhost:5555/posts?order=-title&limit=5&offset=10
```
and so on

#### Local installation
```shell script
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
cd docker-dev
docker-compose -f docker-compose-db.yml up -d
cd ..
hackapp # main entrypoint for run
```

#### Run tests
```shell script
pytest
```
