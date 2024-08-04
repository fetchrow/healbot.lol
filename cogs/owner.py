import discord
import os
import sys
import aiohttp

from discord import Message
from discord.ext import commands
from discord.ext.commands import (
    Cog,
    command,
    hybrid_command,
    is_owner
)
from typing import Union
from discord.ext.tasks import loop
from discord import Member, Guild, Object, User
from asyncio import gather

from tools.heal import Heal
from tools.managers.context import Context 

class Owner(Cog):
    def __init__(self, bot: Heal) -> None:
        self.bot = bot

    @hybrid_command(
        name = "activity",
        aliases = ["status"],
        description = "Change the bots activity status."
    )
    @is_owner()
    
    async def activity(self, ctx: Context, *, activity: str):
        activity = discord.CustomActivity(name=activity)
        await self.bot.change_presence(activity=activity)
        await ctx.approve(f"**Activity** has been set to - `{activity}`")

    @hybrid_command(
        name = "say",
        aliases = ["repeat", "rp"],
        description = "Make the bot repeat the text"
    )
    @is_owner()
    async def say(self, ctx, *, msg: str):
        await ctx.message.delete()
        await ctx.send(msg)

    def restart_bot(self): 
        os.execv(sys.executable, ["python3"] + sys.argv)
        

    @commands.group(
        name = "system",
        aliases = ["sys"],
        description = "System commands."
    )
    @is_owner()
    async def system(self, ctx: Context):
        return None
    
    @system.command(
        name = "restart",
        aliases = ["rs", "reboot"],
        description = "restarts the bot."
    )
    @is_owner()
    async def system_restart(self, ctx: Context):
        await ctx.approve(f"Restarting bot...")
        await self.restart_bot()


    @system.command(
        name = "pfp",
        aliases = ["av", "changeav"]
    )
    @is_owner()
    async def system_avatar(self, ctx: Context, *, image: str= None):

        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        elif image:
            image_url = image
        else:
            return await ctx.warn(f"Please provide an image URL or upload an image.")

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await ctx.deny(f"Failed to fetch the image.")
                data = await resp.read()

        try:
            await self.bot.user.edit(avatar=data)
            await ctx.approve(f"Changed my **pfp** successfully!")
        except discord.HTTPException as e:
            await ctx.deny(f"Failed to change profile picture: {e}")

    @system.command(
        name = "banner",
        aliases = ["bnr", "changebanner"]
    )
    @is_owner()
    async def system_banner(self, ctx: Context, *, image: str= None):

        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        elif image:
            image_url = image
        else:
            return await ctx.warn(f"Please provide an image URL or upload an image.")

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await ctx.deny(f"Failed to fetch the image.")
                data = await resp.read()

        try:
            await self.bot.user.edit(banner=data)
            await ctx.approve(f"Changed my **banner** successfully!")
        except discord.HTTPException as e:
            await ctx.deny(f"Failed to change profile picture: {e}")


    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: Context):

        await ctx.message.add_reaction("⌛")
        await self.bot.tree.sync()
        await ctx.message.clear_reactions()
        return await ctx.message.add_reaction("✅")

    

async def setup(bot: Heal) -> None:
    await bot.add_cog(Owner(bot))
