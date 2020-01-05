from sqlalchemy import Column, ForeignKey, JSON, String
from sqlalchemy.ext.mutable import MutableDict

from sakuya.database.util import Base


class Role(Base):
    __tablename__ = 'roles'
    id = Column(String, primary_key=True)
    guild_id = Column(String, ForeignKey('guilds.id'))
    json = Column(MutableDict.as_mutable(JSON), default={}, nullable=False)
