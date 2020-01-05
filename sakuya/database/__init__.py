from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from sakuya import Config
from sakuya.database.guild import Guild
from sakuya.database.member import Member
from sakuya.database.role import Role
from sakuya.database.user import User
from sakuya.database.util import Base

config = Config['database']
engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(config['username'], config['password'], config['host'],
                                                            config['port'], config['database']))
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

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
