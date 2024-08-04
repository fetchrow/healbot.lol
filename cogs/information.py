import discord
import psutil
import sys
import time
import random
from random import choice

from tools.managers.context     import Context
from discord.ext.commands       import command, group, BucketType, cooldown, has_permissions
from tools.configuration        import Emojis, Colors
from tools.paginator            import Paginator
from discord.utils              import format_dt
from discord.ext                import commands
from tools.heal                 import Heal

class Information(commands.Cog):
    def __init__(self, bot: Heal) -> None:
        self.bot = bot

    @command(
        name = "botinfo",
        aliases = ["bi", "bot"],
        usage = "botinfo"
    )
    @cooldown(1, 5, commands.BucketType.user)
    async def botinfo(self, ctx: Context):
        commands = [command for command in set(self.bot.walk_commands()) if command.cog_name != 'Jishaku']

        embed = discord.Embed(
            title = f"heal",
            color = Colors.BASE_COLOR
        )
        embed.add_field(name="statistics", value=f"> guilds: `{len(self.bot.guilds):,}`\n> users: `{len(self.bot.users):,}`\n> commands: `{len(commands):,}`", inline=False)
        embed.add_field(name="system", value=f"> cpu usage: `{psutil.cpu_percent()}%`\n> ram usage: `{psutil.virtual_memory().percent}%`\n> python version: `{sys.version.split(" (")[0]}`", inline=False)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @command(
        name = "ping",
        aliases = ["heartbeat", "latency", "websocket"],
        usage = "ping"
    )
    @cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: Context):
        list = ["china", "north korea", "your ip", "localhost", "heal", "discord", "your mom"]

        start = time.time()
        message = await ctx.send(content="..")
        finished = time.time() - start

        return await message.edit(
            content=f"it took `{int(self.bot.latency * 1000)}ms` to ping **{choice(list)}** (edit: `{finished:.2f}ms`)"
        )

    @command(
        name = "invite",
        aliases = ["inv"],
        usage = "invite"
    )
    @cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx: Context):
        await ctx.send(f"{discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions(8))}")


async def setup(bot: Heal):
    await bot.add_cog(Information(bot))