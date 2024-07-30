import discord
import sys
import humanfriendly

from tools.managers.context     import Context
from discord.ext.commands       import command, group, BucketType, cooldown, has_permissions
from tools.configuration        import Emojis, Colors
from tools.paginator            import Paginator
from discord.utils              import format_dt
from discord.ext                import commands
from tools.heal                 import Heal

class Moderation(commands.Cog):
    def __init__(self, bot: Heal) -> None:
        self.bot = bot

    @command(
        name = "kick",
        aliases = ["getout", "bye"],
        usage = "kick @fetchrow rule breaker"
    )
    @cooldown(1, 5, BucketType.user)
    @has_permissions(moderate_members=True)
    async def kick(self, ctx: Context, user: discord.Member, *, reason: str = "no reason"):
        reason += ' | executed by {}'.format(ctx.author)
        await ctx.typing()

        try:
            if ctx.author is ctx.guild.owner:
                await user.kick(reason=reason)
                return await ctx.approve(f'Successfully kicked {user.mention} for {reason.split(' |')[0]}')
            if user is ctx.guild.owner:
                return await ctx.warn(f"You're unable to kick the **server owner**.")
            if user is ctx.author:
                return await ctx.warn(f"You're unable to kick **yourself**.")
            if ctx.author.top_role.position <= user.top_role.position:
                return await ctx.warn(f"You're unable to kick a user with a **higher role** than **yourself**.")
            
            await user.kick(reason=reason)
            return await ctx.approve(f'Successfully kicked {user.mention} for {reason.split(' |')[0]}')
        except:
            return await ctx.deny(f'Failed to kick {user.mention}.')
        
    @command(
        name = "ban",
        aliases = ["fuckoff", "banish"],
        usage = "ban @fetchrow raider"
    )
    @cooldown(1, 5, BucketType.user)
    @has_permissions(moderate_members=True)
    async def ban(self, ctx: Context, user: discord.Member, *, reason: str = "no reason"):
        reason += ' | executed by {}'.format(ctx.author)
        await ctx.typing()

        try:
            if user is ctx.guild.owner:
                return await ctx.warn(f"You're unable to ban the **server owner**.")
            if user is ctx.author:
                return await ctx.warn(f"You're unable to ban **yourself**.")
            if ctx.author.top_role.position <= user.top_role.position:
                return await ctx.warn(f"You're unable to ban a user with a **higher role** than **yourself**.")
            
            await user.kick(reason=reason)
            return await ctx.approve(f'Successfully banned {user.mention} for {reason.split(' |')[0]}')
        except:
            return await ctx.deny(f'Failed to ban {user.mention}.')
        
    @commands.command(name='mute', description='mute a user in your server', brief='-mute <user> <time> <reason>')
    @Perms.check_perms('manage_members')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def mute(self, ctx: commands.Context, member: discord.Member = None, time = None, *, reason: str = 'no reason'):
        if member is None: return await ctx.create_pages(ctx.command)
        await ctx.typing()

        if ctx.author is ctx.guild.owner:
            return await ctx.warn("You're unable to mute the **server owner**.")
        if member is ctx.author:
            return await ctx.warn("You're unable to mute **yourself**.")
        if ctx.author.top_role.position <= member.top_role.position:
            return await ctx.warn("You're unable to mute a user with a **higher role** than **yourself**.")
        
        if not time:
            time = '29d'
        
        if not re.match(r'^\d+[smhdw]$', time):
            return await ctx.warn("Please use a valid format (for example: `5s, 10m, 1h, 3d`)")
        
        amount = humanfriendly.parse_timespan(time)
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=amount), reason=reason)
        return await ctx.approve(f'**muted** {member.mention}')
    
    @commands.command(name='unmute', description='ummute a user in your server', brief='-ummute <user> <reason>')
    @Perms.check_perms('manage_members')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unmute(self, ctx: commands.Context, member: discord.Member = None, *, reason: str = 'no reason'):
        if member is None: return await ctx.create_pages(ctx.command)
        await ctx.typing()

        if ctx.author is ctx.guild.owner:
            return await ctx.warn("You're unable to unmute the **server owner**.")
        if member is ctx.author:
            return await ctx.warn("You're unable to unmute **yourself**.")
        if ctx.author.top_role.position <= member.top_role.position:
            return await ctx.warn("You're unable to unmute a user with a **higher role** than **yourself**.")

        await member.timeout(None, reason=reason)
        return await ctx.approve(f'**unmuted** {member.mention}')

async def setup(bot: Heal):
    await bot.add_cog(Moderation(bot))