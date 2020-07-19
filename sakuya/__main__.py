from discord.ext.commands import Bot

from sakuya import Config, generate_embed_template


class Sakuya(Bot):
    def __init__(self):
        super().__init__(command_prefix=Config['discord']['prefix'])

    async def on_command_error(self, ctx, exception):
        embed = generate_embed_template(ctx, 'Error Running Command', True)
        embed.description = str(exception)
        await ctx.send(embed=embed)


bot = Sakuya()
for extension in Config['discord']['extensions'].keys():
    bot.load_extension(extension)
bot.run(Config['discord']['token'])
