from discord import Intents, Member, PermissionOverwrite
from discord.ext.commands import CommandError, Greedy, group, NoPrivateMessage
from discord.utils import get

from sakuya import generate_embed_template, Plugin
from sakuya.database import Guild, session_ctx
from sakuya.database.methods import to_sql

DEFAULT_EXEC_DATA = {}
INTENTS = Intents(guild_messages=True, guilds=True, members=True)


class Exec(Plugin):
    def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()
        return True

    @group(name='exec', brief='Manage exec positions.', invoke_without_command=True)
    async def _exec(self, ctx):
        await ctx.send_help(ctx.command)

    @_exec.command(brief='Add a new exec position.')
    async def add(self, ctx, position: str):
        with session_ctx() as session:
            obj = to_sql(session, ctx.guild, Guild)
            data = self.get_data(obj, DEFAULT_EXEC_DATA)
            if position in data:
                raise CommandError('Exec position `{}` already exists'.format(position))
            else:
                data[position] = {
                    'current': [],
                    'previous': []
                }
                self.set_data(session, obj, data)
                embed = generate_embed_template(ctx, 'Exec Position Added Successfully')
                embed.description = position
                await ctx.send(embed=embed)

    @_exec.command(name='list', brief='List all exec positions.')
    async def _list(self, ctx):
        with session_ctx() as session:
            obj = to_sql(session, ctx.guild, Guild)
            data = self.get_data(obj, DEFAULT_EXEC_DATA)
        embed = generate_embed_template(ctx, 'List of Exec Positions')
        positions = []
        for position, officers in data.items():
            current = []
            previous = []
            for member_id in officers['current']:
                member = get(ctx.guild.members, id=member_id)
                current.append(member.mention)
            for member_id in officers['previous']:
                member = get(ctx.guild.members, id=member_id)
                previous.append(member.mention)
            positions.append('{}. {} - {} (previously {})'.format(str(len(positions) + 1), position, ', '.join(current)
                                                                  if current else 'None', ', '.join(previous) if
                                                                  previous else 'None'))
        embed.description = '\n'.join(positions) if positions else ('No positions. Add positions with the '
                                                                    '`{}exec add` command!').format(ctx.prefix)
        await ctx.send(embed=embed)

    @_exec.command(name='set', brief='Set the officers that belong to a certain exec position (and handle channels '
                                     'accordingly).')
    async def _set(self, ctx, position: str, officers: Greedy[Member]):
        with session_ctx() as session:
            obj = to_sql(session, ctx.guild, Guild)
            data = self.get_data(obj, DEFAULT_EXEC_DATA)
            if pos_data := data.get(position):
                pos_data['previous'] = pos_data['current']
                pos_data['current'] = []
                self.set_data(session, obj, data)

                role = get(ctx.guild.roles, name='Exec')
                for officer in officers:
                    pos_data['current'].append(officer.id)
                    await officer.add_roles(role)

                category = get(ctx.guild.categories, name='Exec')
                previous = get(ctx.guild.categories, name='Previous Exec')
                if not (category and previous):
                    raise CommandError('Could not find `Exec` channel category (did you run the `{}exec setup` '
                                       'command?'.format(ctx.prefix))
                reason = 'Update officers for {}'.format(position)
                if channel := get(category.text_channels, name=position):
                    await channel.edit(category=previous, reason=reason)
                overwrites = {officer: PermissionOverwrite(read_messages=True) for officer in officers}
                overwrites[ctx.guild.default_role] = PermissionOverwrite(read_messages=False)
                overwrites[ctx.me] = PermissionOverwrite(read_messages=True)
                await ctx.guild.create_text_channel(position, overwrites=overwrites, category=category, reason=reason)

                embed = generate_embed_template(ctx, 'Position Officers Set Successfully')
                embed.add_field(name='Position', value=position)
                embed.add_field(name='Current', value=', '.join([officer.mention for officer in officers]) if officers
                                                      else 'None')
                previous = pos_data['previous']
                embed.add_field(name='Previous', value=', '.join([get(ctx.guild.members, id=officer).mention for
                                                                 officer in previous]) if previous else 'None')
                await ctx.send(embed=embed)
            else:
                raise CommandError('Exec position `{}` does not exist'.format(position))

    @_exec.command(brief='Set up the exec plugin by creating the appropriate categories.')
    async def setup(self, ctx):
        reason = 'Create categories for exec plugin'
        role = get(ctx.guild.roles, name='Exec')
        overwrites = {
            ctx.guild.default_role: PermissionOverwrite(read_messages=False),
            ctx.me: PermissionOverwrite(read_messages=True),
            role: PermissionOverwrite(read_messages=True)
        }
        if category := get(ctx.guild.categories, name='Exec'):
            await category.edit(overwrites=overwrites, reason=reason)
        else:
            await ctx.guild.create_category('Exec', overwrites=overwrites, reason=reason)
        if category := get(ctx.guild.categories, name='Previous Exec'):
            await category.edit(overwrites=overwrites, reason=reason)
        else:
            await ctx.guild.create_category('Previous Exec', overwrites=overwrites, reason=reason)
        embed = generate_embed_template(ctx, 'Exec Plugin Setup Complete')
        await ctx.send(embed=embed)

    @_exec.command(brief='Complete exec transition by deleting previous exec channels.')
    async def transition(self, ctx):
        if category := get(ctx.guild.categories, name='Previous Exec'):
            for channel in category.text_channels:
                await channel.delete(reason='Complete transition from previous exec to new exec')
            embed = generate_embed_template(ctx, 'Exec Transition Completed Successfully')
            await ctx.send(embed=embed)
        else:
            raise CommandError('Could not find `Previous Exec` channels (did you run the `{}exec setup` command?)'
                               .format(ctx.prefix))


def setup(bot):
    bot.add_cog(Exec())


def teardown(bot):
    bot.remove_cog('Exec')
