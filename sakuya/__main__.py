from discord import Intents
from discord.ext.commands import Bot

from sakuya import Config, generate_embed_template

from importlib import import_module
from logging import getLogger

logger = getLogger(__name__)


class Sakuya(Bot):
    def __init__(self, intents):
        super().__init__(command_prefix=Config['discord']['prefix'], intents=intents)

    async def on_command_error(self, ctx, exception):
        logger.warning('error running command {}:'.format(ctx.message.content), exc_info=exception)
        embed = generate_embed_template(ctx, 'Error Running Command', True)
        embed.description = str(exception)
        await ctx.send(embed=embed)


plugin_intents = Intents()
for extension in Config['discord']['extensions'].keys():
    plugin_intents.value |= import_module(extension).INTENTS.value

bot = Sakuya(plugin_intents)
for extension in Config['discord']['extensions'].keys():
    bot.load_extension(extension)
bot.run(Config['discord']['token'])
