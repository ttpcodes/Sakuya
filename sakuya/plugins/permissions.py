from discord import Member as DiscordMember, Role as DiscordRole
from discord.ext.commands import CheckFailure, CommandError, Group, group, NoPrivateMessage
from discord.utils import get

from sakuya import generate_embed_template, Plugin
from sakuya.database import Guild, Member, Role, Session
from sakuya.database.methods import to_sql

import typing

DEFAULT_ROLE_USER_DATA = []


class MissingPermissions(CheckFailure):
    def __init__(self, *args):
        super().__init__('You do not have permission to run this command.', *args)


class Permissions(Plugin):
    def bot_check(self, ctx):
        if isinstance(ctx.command, Group) or not ctx.guild:
            return True
        member = get(ctx.guild.members, id=ctx.author.id)
        if member.guild_permissions.administrator:
            return True
        allowed = False
        session = Session()
        obj = to_sql(session, member, Member)
        data = self.get_data(obj, DEFAULT_ROLE_USER_DATA)
        attributes = []
        if ctx.cog:
            attributes.append(ctx.cog.qualified_name.lower())
        if ctx.invoked_subcommand:
            attributes.append(ctx.invoked_subcommand.parent.name.lower())
        attributes.append(ctx.command.name.lower())
        permission = '.'.join(attributes)
        if not any([node in [permission, '*'] or permission.startswith(node) and permission[len(node)] == '.' for node
                    in data]):
            for role in member.roles:
                obj = to_sql(session, role, Role)
                data = self.get_data(obj, DEFAULT_ROLE_USER_DATA)
                if any([node in [permission, '*'] or permission.startswith(node) and permission[len(node)] == '.' for
                        node in data]):
                    allowed = True
                    break
        else:
            allowed = True
        session.close()
        if not allowed:
            raise MissingPermissions()
        return True

    def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()
        return True

    @group()
    async def permissions(self, ctx):
        pass

    @permissions.command()
    async def add(self, ctx, target: typing.Union[DiscordRole, DiscordMember], permission: str):
        session = Session()
        obj, target_type = validate_permissions_command(session, target, permission)
        data = self.get_data(obj, DEFAULT_ROLE_USER_DATA)
        if permission in data:
            session.close()
            raise CommandError('{} `{}` already has permission `{}`'.format(target_type, str(target), permission))
        else:
            data.append(permission)
            self.set_data(session, obj, data)
            embed = generate_embed_template(ctx, 'Permissions Binding Added Successfully')
            set_permissions_embed(embed, target_type, target, permission)
            session.close()
            await ctx.send(embed=embed)

    @permissions.command()
    async def remove(self, ctx, target: typing.Union[DiscordMember, DiscordRole], permission: str):
        session = Session()
        obj, target_type = validate_permissions_command(session, target, permission)
        data = self.get_data(obj, DEFAULT_ROLE_USER_DATA)
        if permission in data:
            data.remove(permission)
            self.set_data(session, obj, data)
            embed = generate_embed_template(ctx, 'Permissions Binding Removed Successfully')
            set_permissions_embed(embed, target_type, target, permission)
            session.close()
            await ctx.send(embed=embed)
        else:
            session.close()
            raise CommandError('Could not find {} `{}` with permission `{}`'.format(target_type.lower(), str(target),
                                                                                    permission))

    @permissions.command()
    async def reset(self, ctx):
        session = Session()
        obj = to_sql(session, ctx.guild, Guild)
        for member in obj.members:
            self.set_data(session, member, DEFAULT_ROLE_USER_DATA)
        for role in obj.roles:
            self.set_data(session, role, DEFAULT_ROLE_USER_DATA)
        embed = generate_embed_template(ctx, 'Permissions Bindings Reset Successfully')
        embed.description = 'You may now set up your permissions again.'
        await ctx.send(embed=embed)


def set_permissions_embed(embed, target_type, target, permission):
    embed.add_field(name='Type', value=target_type, inline=True)
    embed.add_field(name='Name', value=str(target), inline=True)
    embed.add_field(name='Permission', value=permission)


def validate_permissions_command(session, target, permission):
    if len(permission) == 0:
        raise CommandError("An empty permission string was specified")
    if isinstance(target, DiscordMember):
        obj = to_sql(session, target, Member)
        target_type = 'Member'
    else:
        obj = to_sql(session, target, Role)
        target_type = 'Role'
    return obj, target_type


def setup(bot):
    bot.add_cog(Permissions())


def teardown(bot):
    bot.remove_cog('Permissions')
