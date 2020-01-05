from sqlalchemy import Column, JSON, String
from sqlalchemy.ext.mutable import MutableDict

from sakuya.database.util import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    json = Column(MutableDict.as_mutable(JSON), default={}, nullable=False)
