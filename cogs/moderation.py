import discord
import sys
import humanfriendly
import re 
import datetime

from tools.managers.context     import Context
from discord.ext.commands       import command, group, BucketType, has_permissions
from tools.configuration        import Emojis, Colors
from tools.paginator            import Paginator
from discord.utils              import format_dt
from discord.ext                import commands
from tools.heal                 import Heal

class Moderation(commands.Cog):
    def __init__(self, bot: Heal) -> None:
        self.bot = bot

    @command(
        name = "lock",
        usage = "lock #channel"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @has_permissions(manage_channels = True)
    async def lock(self, ctx: Context, *, channel: discord.TextChannel = None):

        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.approve('Channel has been locked.')

    @command(
        name = "unlock",
        usage = "unlock #channel"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @has_permissions(manage_channels = True)
    async def unlock(self, ctx: Context, *, channel: discord.TextChannel = None):

        if channel is None:
            channel = ctx.channel

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.approve('Channel has been unlocked.')

    @command(
        name = "kick",
        aliases = ["getout", "bye"],
        usage = "kick @fetchrow rule breaker"
    )
    @commands.cooldown(1, 5, BucketType.user)
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
    @commands.cooldown(1, 5, BucketType.user)
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
            
            await user.ban(reason=reason)
            return await ctx.approve(f'Successfully banned {user.mention} for {reason.split(' |')[0]}')
        except:
            return await ctx.deny(f'Failed to ban {user.mention}.')
        
    @commands.command(name='mute', description='mute a user in your server', brief='-mute <user> <time> <reason>')
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def mute(self, ctx: Context, user: discord.Member, time: str="60s", *, reason: str = "No reason provided"):
        
        if user.id == self.bot.user.id:
            return await ctx.deny("I cannot **mute** myself.")

        if user.id == ctx.author.id:
            return await ctx.deny("You cannot **mute** yourself.")


        member = ctx.guild.get_member(user.id)
        if member:

            if ctx.author.id != ctx.guild.owner_id:
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    return await ctx.warn("You cannot **mute** a member with a higher role than me.")
                if member.top_role.position >= ctx.author.top_role.position:
                    return await ctx.warn("You cannot **mute** a member with a higher role than you.")
        else:
            pass
        
        time = humanfriendly.parse_timespan(time)

        await user.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=time), reason=reason)

        if reason:

            await ctx.approve(f"Muted **{user}** for `{humanfriendly.format_timespan(time)}` - **{reason}**")
    
    @commands.command(name='unmute', description='ummute a user in your server', brief='-ummute <user> <reason>')
    @commands.has_permissions(moderate_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unmute(self, ctx: commands.Context, user: discord.Member, *, reason: str = "No reason provided"):
        
        if user.id == self.bot.user.id:
            return await ctx.deny("I cannot **mute** myself.")

        if user.id == ctx.author.id:
            return await ctx.deny("You cannot **mute** yourself.")


        member = ctx.guild.get_member(user.id)
        if member:

            if ctx.author.id != ctx.guild.owner_id:
                if member.top_role.position >= ctx.guild.me.top_role.position:
                    return await ctx.warn("You cannot **mute** a member with a higher role than me.")
                if member.top_role.position >= ctx.author.top_role.position:
                    return await ctx.warn("You cannot **mute** a member with a higher role than you.")
        else:
            pass
        

        await user.timeout(None, reason=reason)

        if reason:

            await ctx.approve(f"Unmuted **{user}**")
    
    @commands.group(name='thread', description='manage threads using a single command', invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_threads=True)
    async def thread(self, ctx: commands.Context):
        await ctx.send("help")

    @thread.command(name="lock", description="lock a thread")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_threads=True)
    async def thread_lock(self, ctx: Context, thread: discord.Thread = None):
        if thread is None: return await ctx.create_pages(ctx.command)
        await thread.lock()
        return await ctx.approve(f'**locked** {thread.mention}')
    
    @thread.command(name="delete", description="delete a thread")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_threads=True)
    async def thread_delete(self, ctx: Context, thread: discord.Thread = None):
        if thread is None: return await ctx.create_pages(ctx.command)
        await thread.delete()
    
    @thread.command(name="unlock", description="unlock a thread")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_threads=True)
    async def thread_unlock(self, ctx: Context, thread: discord.Thread = None):
        if thread is None: return await ctx.create_pages(ctx.command)
        await thread.unlock()
        return await ctx.approve(f'**unlocked** {thread.mention}')
    
    @command(name="cooldown", description="set a channel cooldown")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def cooldown(self, ctx :Context, seconds: int = 0, channel: discord.TextChannel = None):
        if channel is None: channel = ctx.channel

        await channel.edit(slowmode_delay=seconds)
        return await ctx.approve(f'**set cooldown** to {seconds} seconds in {channel.mention}')
        

async def setup(bot: Heal):
    await bot.add_cog(Moderation(bot))