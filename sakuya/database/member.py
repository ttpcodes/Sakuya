from sqlalchemy import Column, ForeignKey, JSON, String
from sqlalchemy.ext.mutable import MutableDict

from sakuya.database.util import Base


class Member(Base):
    __tablename__ = 'members'
    guild_id = Column(String, ForeignKey('guilds.id'), primary_key=True)
    id = Column(String, ForeignKey('users.id'), primary_key=True)
    json = Column(MutableDict.as_mutable(JSON), default={}, nullable=False)
