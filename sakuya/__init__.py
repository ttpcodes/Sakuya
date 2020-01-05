from copy import deepcopy
from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog
from json import load

with open('config.json') as fp:
    Config = load(fp)


class Plugin(Cog):
    def get_data(self, obj, default):
        return obj.json.get(self.__class__.__name__, deepcopy(default))

    def set_data(self, session, obj, data):
        obj.json[self.__class__.__name__] = data
        session.commit()


def generate_embed_template(ctx, title, error=False):
    embed = Embed(colour=16711680 if error else 32768, title=title)
    embed.timestamp = datetime.utcnow()
    embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url))
    embed.set_footer(text=str(ctx.me), icon_url=str(ctx.me.avatar_url))
    return embed
