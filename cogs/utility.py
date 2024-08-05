import discord
import sys
import aiohttp

from tools.managers.context     import Context
from discord.ext.commands       import command, group, BucketType, cooldown, has_permissions
from tools.configuration        import Emojis, Colors
from tools.paginator            import Paginator
from discord.utils              import format_dt
from discord.ext                import commands
from tools.heal                 import Heal
from tools.EmbedBuilder         import EmbedBuilder, EmbedScript
from discord.ui import View, Button

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
            return await ctx.warn('there are no **bans** in this server.')

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
            return await ctx.warn('There are no **bots** in this server.')

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

    @commands.command(
        name = "createembed",
        aliases = ["ce"],
        description = "Create an embed."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createembed(self, ctx: Context,  *, code: EmbedScript):
        await ctx.send(**code)

    @commands.command(name = "avatar", aliases = ["av"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx: Context, user: discord.Member = None):
        if user is None:
            user = ctx.author
        embed = discord.Embed(title = f"{user}'s avatar.", color = Colors.BASE_COLOR)
        embed.set_image(url = user.avatar.url)
        view = View()
        view.add_item(Button(label="avatar", url=user.avatar.url))
        await ctx.send(embed=embed, view=view)

    @command(
        name = "chatgpt",
        aliases = ["openai", "ai", "ask"],
        description = "Ask chatgpt a question."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def chatgpt(self, ctx: Context, *, prompt: str):
        await ctx.typing()
        api_url = f"https://api.kastg.xyz/api/ai/llamaV3?prompt={prompt}"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.kastg.xyz/api/ai/llamaV3?prompt={prompt} ") as r:
                response = await r.json()
                await ctx.send(response["result"][0]["response"])
                


async def setup(bot: Heal):
    await bot.add_cog(Utility(bot))