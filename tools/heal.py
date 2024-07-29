import importlib
import jishaku
import logging
import asyncpg
import asyncio
import aiohttp
import discord
import glob
import json
import sys
import os
import re

from tools.managers.context       import Context
from discord.ext                  import commands
from discord                      import Message, Embed

intents = discord.Intents.all()
intents.presences = False

class Heal(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix      = ';',
            help_command        = None,
            intents             = intents,
            allowed_mentions    = discord.AllowedMentions(
                everyone     = False,
                users        = True,
                roles        = False,
                replied_user = False
            ),
            case_insensitive = True,
            owner_ids = [1185934752478396528]
        )

    async def load_modules(self, directory: str) -> None:
        for module in glob.glob(f'{directory}/**/*.py', recursive=True):
            if module.endswith('__init__.py'): continue
            try:
                print(module.replace('\\', '.').replace('.py', ''))
                await self.load_extension(module.replace('\\', '.').replace('.py', ''))
                print(f'Loaded module: {module}')
            except commands.ExtensionFailed:
                print(f'Extension failed to load: {module}')
            except Exception as e:
                print(e)
    
    async def load_patches(self) -> None:
        for module in glob.glob('tools/patches/**/*.py', recursive=True):
            if module.endswith('__init__.py'):
                continue
            
            module_name = module.replace(os.path.sep, '.').replace('/', '.').replace('.py', '')
            
            try:
                importlib.import_module(module_name)
                print(f'Patched: {module}')
            except ModuleNotFoundError as e:
                print(f"Error importing {module_name}: {e}")

    async def setup_hook(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        self.session = aiohttp.ClientSession()

        await self.load_modules('cogs')
        await self.load_extension('jishaku')

    async def get_context(self, message: Message, *, cls=Context):
        return await super().get_context(message, cls=cls)
    
    async def on_command_error(self, ctx: Context, ex: commands.CommandError) -> None:
        if isinstance(ex, commands.errors.NotOwner):
            return await ctx.deny(f'You are not an owner of {self.user.mention}.')
        if isinstance(ex, commands.errors.CommandOnCooldown):
            return await ctx.warn(f'This command is currently on cooldown, try again in ')