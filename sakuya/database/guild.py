from sqlalchemy import Column, JSON, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from sakuya.database.util import Base


class Guild(Base):
    __tablename__ = 'guilds'
    id = Column(String, primary_key=True)
    json = Column(MutableDict.as_mutable(JSON), default={}, nullable=False)
    members = relationship('Member')
    roles = relationship('Role')
