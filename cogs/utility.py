import discord
import sys

from tools.managers.context     import Context
from discord.ext.commands       import command, group, BucketType, cooldown, has_permissions
from tools.configuration        import Emojis, Colors
from tools.paginator            import Paginator
from discord.utils              import format_dt
from discord.ext                import commands
from tools.heal                 import Heal

class Utility(commands.Cog):
    def __init__(self, bot: Heal) -> None:
        self.bot = bot

    @command(
        name="bans",
        aliases=["banlist"],
        usage="bans"
    )
    @cooldown(1, 5, BucketType.user)
    async def bans(self, ctx: Context):
        banned = [m async for m in ctx.guild.bans()]
        count = 0
        embeds = []

        if len(banned) == 0:
            return await ctx.send('there are no **bans** in this server.')

        entries = [
            f"` {i} `  **{m.user.name}**  ({m.user.id})  |  {m.reason if m.reason else 'no reason provided'}"
            for i, m in enumerate(banned, start=1)
        ]

        embed = discord.Embed(color=Colors.BASE_COLOR, title=f"ban list ({len(entries)})", description="")

        for entry in entries:
            embed.description += f'{entry}\n'
            count += 1

            if count == 10:
                embeds.append(embed)
                embed = discord.Embed(color=Colors.BASE_COLOR, description="", title=f"ban list ({len(entries)})")
                count = 0

        if count > 0:
            embeds.append(embed)

        await ctx.paginate(embeds)

    @command(
        name = "boosters",
        aliases = ["blist", "boosterlist"],
        usage = "boosters"
    )
    @cooldown(1, 5, BucketType.user)
    async def boosters(self, ctx: Context):
        boosters = ctx.guild.premium_subscriber_role.members

        count    = 0
        embeds   = []

        if not ctx.guild.premium_subscriber_role or len(ctx.guild.premium_subscriber_role.members) == 0:
            return await ctx.warn('there are no **boosters** in this server.')
        
        entries = [
            f"` {i} `  **{b.name}**  ({b.id})"
            for i, b in enumerate(boosters, start=1)
        ]

        embed = discord.Embed(color=Colors.BASE_COLOR, title=f"booster list ({len(entries)})", description="")

        for entry in entries:
            embed.description += f'{entry}\n'
            count += 1

            if count == 10:
                embeds.append(embed)
                embed = discord.Embed(color=Colors.BASE_COLOR, description="", title=f"booster list ({len(entries)})")
                count = 0

        if count > 0:
            embeds.append(embed)

        await ctx.paginate(embeds)

    @command(
        name = "roles",
        aliases = ["rlist", "rolelist"],
        usage = "roles"
    )
    @cooldown(1, 5, BucketType.user)
    async def roles(self, ctx: Context):
        roles    = ctx.guild.roles
        count    = 0
        embeds   = []

        if len(ctx.guild.roles) == 0:
            return await ctx.warn('there are no **roles** in this server.')
        
        entries = [
            f"` {i} `  {r.mention}  -  {discord.utils.format_dt(r.created_at, style="R")}  |  ({len(r.members)} members)"
            for i, r in enumerate(roles, start=1)
        ]

        embed = discord.Embed(color=Colors.BASE_COLOR, title=f"role list ({len(entries)})", description="")

        for entry in entries:
            embed.description += f'{entry}\n'
            count += 1

            if count == 10:
                embeds.append(embed)
                embed = discord.Embed(color=Colors.BASE_COLOR, description="", title=f"role list ({len(entries)})")
                count = 0

        if count > 0:
            embeds.append(embed)

        await ctx.paginate(embeds)

    @command(
        name = "bots",
        aliases = ["botlist"],
        usage = "bots"
    )
    @cooldown(1, 5, BucketType.user)
    async def bots(self, ctx: Context):
        bots = [member for member in ctx.guild.members if member.bot]
        count = 0
        embeds = []

        if len(bots) == 0:
            return await ctx.send('There are no **bots** in this server.')

        entries = [
            f"` {i} `  **{b.name}**  (`{b.id}`)"
            for i, b in enumerate(bots, start=1)
        ]

        embed = discord.Embed(color=Colors.BASE_COLOR, title=f"Bot list ({len(entries)})", description="")

        for entry in entries:
            embed.description += f'{entry}\n'
            count += 1

            if count == 10:
                embeds.append(embed)
                embed = discord.Embed(color=Colors.BASE_COLOR, description="", title=f"Bot list ({len(entries)})")
                count = 0

        if count > 0:
            embeds.append(embed)

        for e in embeds:
            await ctx.paginate(embeds)

    @commands.Cog.listener("on_message_edit")
    async def process_edits(self, before: discord.Message, after: discord.Message) -> discord.Message:

            if before.content != after.content:
                await self.bot.process_commands(after)

async def setup(bot: Heal):
    await bot.add_cog(Utility(bot))