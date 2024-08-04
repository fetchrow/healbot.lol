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

    @command(
        name = "help",
        aliases = ["h"],
        usage = "help"
    )
    @cooldown(1, 5, commands.BucketType.user)
    async def help(self, ctx: commands.Context):
            options = [
                discord.SelectOption(label="home", description="homepage", emoji="<:aadns:1264995683233173668>"),
                discord.SelectOption(label="Moderation", description="admin commands", emoji="<:aadns:1264995683233173668>"),
                discord.SelectOption(label="Information", description="information commands", emoji="<:aadns:1264995683233173668>"),
                discord.SelectOption(label="Music", description="music commands", emoji="<:aadns:1264995683233173668>"),
                discord.SelectOption(label="Fun", description="fun commands", emoji="<:aadns:1264995683233173668>"),
                discord.SelectOption(label="Utility", description="utility commands", emoji="<:aadns:1264995683233173668>")
            ]

            embed = discord.Embed(color=Colors.BASE_COLOR, description=f"> Use the select menu below to **navigate** throughout the help menu.\n> If your **stuck**, feel free to dm **@psutil** for help.")
            embed.set_thumbnail(url = self.bot.user.avatar)
            embed.set_author(name = self.bot.user.name, icon_url= self.bot.user.avatar)
            select = discord.ui.Select(placeholder="select the category..", options=options)

            async def select_callback(interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id: return await ctx.interaction.deny(message="You are not the author of the embed", empheral=True)
                if select.values[0] == "home": await interaction.response.edit_message(embed=embed)
                else:
                    cmds = []
                    for cmd in set(self.bot.walk_commands()):
                        if cmd.cog_name == select.values[0]:
                            if cmd.parent is not None: cmds.append("{} {}".format(str(cmd.parent), cmd.name))
                            else: cmds.append(cmd.name)

                    eeembed = discord.Embed(color=Colors.BASE_COLOR, description=f"**{select.values[0]} commands**\n```{', '.join(cmds)}```")
                    eeembed.set_thumbnail(url = self.bot.user.avatar)
                    await interaction.response.edit_message(embed=eeembed)

            select.callback = select_callback
            view = discord.ui.View()
            view.add_item(select)

            await ctx.send(embed=embed, view=view)

    @command(
        name = "uptime",
        aliases = ["up"],
        usage = "uptime"
    )
    @cooldown(1, 5, commands.BucketType.user)
    async def uptime(self, ctx: Context):
        await ctx.neutral(f":alarm_clock: I have been **online** for {self.bot._uptime}")
        

async def setup(bot: Heal):
    await bot.add_cog(Information(bot))