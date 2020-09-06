from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from urllib.parse import quote_plus

from sakuya import Config
from sakuya.database.guild import Guild
from sakuya.database.member import Member
from sakuya.database.role import Role
from sakuya.database.user import User
from sakuya.database.util import Base

from contextlib import contextmanager

config = Config['database']
engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(quote_plus(config['username']),
                                                            quote_plus(config['password']), quote_plus(config['host']),
                                                            quote_plus(str(config['port'])),
                                                            quote_plus(config['database'])))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@contextmanager
def session_ctx():
    instance = Session()
    yield instance
    instance.close()


mappings = {
    'Guild': Guild,
    'Member': {
        'parent': {
            'attribute': 'guild.id',
            'column': 'guild_id',
            'model': Guild
        },
        'child': User,
        'model': Member
    },
    'Role': {
        'parent': {
            'attribute': 'guild.id',
            'column': 'guild_id',
            'model': Guild
        },
        'model': Role
    },
    'User': User
}
