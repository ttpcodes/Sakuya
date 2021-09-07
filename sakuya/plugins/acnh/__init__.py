from discord import Intents
from discord.ext.commands import BadArgument, Converter, group
from grpc import insecure_channel

from sakuya import Config, generate_embed_template, Plugin
from sakuya.plugins.acnh.proto.meteonook_pb2 import Hemisphere as ProtoHemisphere, IslandInfo
from sakuya.plugins.acnh.proto.meteonook_pb2_grpc import MeteoNookStub

DEFAULT_ISLAND_NAME = 'Default'
INTENTS = Intents(dm_messages=True, guild_messages=True, members=True)
WAIT_SECONDS = 10


config = Config['discord']['extensions']['sakuya.plugins.acnh']


class Hemisphere(Converter):
    async def convert(self, ctx, arg):
        lower = arg.lower()
        if lower in {'n', 'north'}:
            return ProtoHemisphere.NORTH
        elif lower in {'s', 'south'}:
            return ProtoHemisphere.SOUTH
        else:
            raise BadArgument()


class ACNH(Plugin):
    @group(brief='Animal Crossing: New Horizons related commands.', invoke_without_command=True)
    async def acnh(self, ctx):
        await ctx.send_help(ctx.command)

    @acnh.group(brief='Commands related to weather.', invoke_without_command=True)
    async def weather(self, ctx):
        await ctx.send_help(ctx.command)

    @weather.command(brief='Look up weather for a particular seed.')
    async def lookup(self, ctx, seed: int, hemisphere: Hemisphere):
        channel = insecure_channel('{}:{}'.format(config['weather']['host'], config['weather']['port']))
        stub = MeteoNookStub(channel)
        island = IslandInfo(seed=seed, hemisphere=hemisphere)
        overview_future = stub.GetOverview.future(island)
        overview = overview_future.result()

        embed = generate_embed_template(ctx, "Today's Weather for {}".format(seed))
        embed.description = overview.forecast
        embed.add_field(name='Pattern', value=overview.pattern, inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ACNH())


def teardown(bot):
    bot.remove_cog('ACNH')
