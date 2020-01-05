from discord import Role as DiscordRole
from discord.ext.commands import CommandError, group, NoPrivateMessage

from sakuya import generate_embed_template, Plugin
from sakuya.database import Role, Session
from sakuya.database.methods import to_sql

DEFAULT_ROLE_DATA = False


class Roles(Plugin):
    def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()
        return True

    @group()
    async def roles(self, ctx):
        pass

    @roles.command()
    async def add(self, ctx, role: DiscordRole):
        session = Session()
        obj = to_sql(session, role, Role)
        data = self.get_data(obj, DEFAULT_ROLE_DATA)
        session.close()
        if data:
            if role in ctx.author.roles:
                raise CommandError('You already have the role `{}`'.format(str(role)))
            await ctx.author.add_roles(role, reason='Added via command')
            embed = generate_embed_template(ctx, 'Role Add Successfully')
            embed.description = str(role)
            await ctx.send(embed=embed)
            return
        raise CommandError('You are not allowed to add role {}'.format(str(role)))

    @roles.command()
    async def allow(self, ctx, role: DiscordRole):
        session = Session()
        obj = to_sql(session, role, Role)
        data = self.get_data(obj, DEFAULT_ROLE_DATA)
        if data:
            session.close()
            raise CommandError('Role `{}` is already allowed'.format(str(role)))
        self.set_data(session, obj, True)
        session.close()
        embed = generate_embed_template(ctx, 'Role Allowed Successfully')
        embed.description = str(role)
        await ctx.send(embed=embed)

    @roles.command()
    async def disallow(self, ctx, role: DiscordRole):
        session = Session()
        obj = to_sql(session, role, Role)
        data = self.get_data(obj, DEFAULT_ROLE_DATA)
        if data:
            self.set_data(session, obj, False)
            session.close()
            embed = generate_embed_template(ctx, 'Role Disallowed Successfully')
            embed.description = str(role)
            await ctx.send(embed=embed)
            return
        session.close()
        raise CommandError('Role `{}` is already disallowed'.format(str(role)))

    @roles.command()
    async def remove(self, ctx, role: DiscordRole):
        session = Session()
        obj = to_sql(session, role, Role)
        data = self.get_data(obj, DEFAULT_ROLE_DATA)
        session.close()
        if data:
            if role in ctx.author.roles:
                await ctx.author.remove_roles(role, reason='Removed via command')
                embed = generate_embed_template(ctx, 'Role Removed Successfully')
                embed.description = str(role)
                await ctx.send(embed=embed)
                return
            raise CommandError("You already don't have the role `{}`".format(str(role)))
        raise CommandError('You are not allowed to remove role {}'.format(str(role)))


def setup(bot):
    bot.add_cog(Roles())


def teardown(bot):
    bot.remove_cog('Roles')
