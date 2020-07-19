from discord.ext.commands import command

from sakuya import Config, generate_embed_template, Plugin
from sakuya.database import Guild, Session
from sakuya.database.methods import to_sql


DEFAULT_PREFIX = Config['discord']['prefix']


class Prefix(Plugin):
    @command(brief='Set the command prefix in this guild.')
    async def prefix(self, ctx, prefix: str):
        session = Session()
        obj = to_sql(session, ctx.guild, Guild)
        self.set_data(session, obj, prefix)
        session.close()

        embed = generate_embed_template(ctx, 'Command Prefix Set Successfully')
        embed.description = prefix
        await ctx.send(embed=embed)

    def get_prefix(self, _, message):
        session = Session()
        obj = to_sql(session, message.guild, Guild)
        prefix = self.get_data(obj, DEFAULT_PREFIX)
        session.close()
        return prefix


def setup(bot):
    instance = Prefix()
    bot.add_cog(instance)
    bot.command_prefix = instance.get_prefix


def teardown(bot):
    bot.remove_cog('Prefix')
    bot.command_prefix = DEFAULT_PREFIX
