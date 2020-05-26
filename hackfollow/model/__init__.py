from dataclasses import dataclass

from loguru import logger
from sqla_wrapper import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.exc import SQLAlchemyError

from hackfollow import settings
from hackfollow.model.magic.utils import db_session_scope


def db_uri_config():
    if settings.test:
        return settings.db_uri_test
    return settings.db_uri


db = SQLAlchemy(db_uri_config(), scopefunc=db_session_scope)


@dataclass
class Link:
    title: str
    url: str

    def __str__(self):
        return f'{self.title} - {self.url}'

    def __repr__(self):
        return self.__str__()


class BaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def get_by_id(cls, model_id):
        try:
            return db.query(cls).get(model_id)
        except SQLAlchemyError:
            logger.exception()
            raise

    @classmethod
    def get_sort_field(cls, query, field_name):
        field = getattr(cls, field_name)
        nullable = getattr(field, "nullable", False)
        return query, field, nullable

    @classmethod
    def replace_id(cls):
        raise NotImplemented

    @classmethod
    def sort_query(cls, query, sort):
        fields = []

        for field_name in sort:
            name = field_name
            is_desc = False
            if field_name.startswith('-'):
                name = field_name[1:]
                is_desc = True
            if name == "id":
                name = cls.replace_id()

            query, field, nullable = cls.get_sort_field(query, name)

            if is_desc:
                field = field.desc()
            if nullable:
                if is_desc:
                    field = field.nullslast()
                else:
                    field = field.nullsfirst()

            fields.append(field)

        query = query.order_by(*fields)
        return query


class LinkModel(BaseModel):
    link_id = Column(Integer, primary_key=True)
    url = Column(String(length=4096))
    title = Column(String(length=4096))
    created = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)

    @classmethod
    def create(cls, link: Link):
        """Return LinkModel and whether item was created"""
        link_exist = db.query(cls).filter(cls.url == link.url).one_or_none()
        if link_exist:
            return link_exist, False
        return cls(url=link.url, title=link.title), True

    def to_dict(self):
        return {
            'id': self.link_id,
            'title': self.title,
            'url': self.url,
            'created': str(self.created),
        }

    @classmethod
    def replace_id(cls):
        return 'link_id'
