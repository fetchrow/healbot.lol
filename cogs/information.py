import discord
import psutil
import sys

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
    @cooldown(1, 2, commands.BucketType.user)
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

async def setup(bot: Heal):
    await bot.add_cog(Information(bot))