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
import datetime

from tools.managers.context       import Context
from tools.managers.lastfm        import Handler
from discord.ext                  import commands
from discord                      import Message, Embed

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
            owner_ids = [1185934752478396528, 187747524646404105]
        )

    async def load_modules(self, directory: str) -> None:
        for module in glob.glob(f'{directory}/**/*.py', recursive=True):
            if module.endswith('__init__.py'): continue
            try:
                await self.load_extension(module.replace('/', '.').replace('.py', ''))
                log.info(f'Loaded module: {module}')
            except commands.ExtensionFailed:
                log.warning(f'Extension failed to load: {module}')
            except:
                pass
    
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

    async def on_ready(self) -> None:
        log.info(f'Logged in as {self.user.name}#{self.user.discriminator} ({self.user.id})')
        log.info(f'Connected to {len(self.guilds)} guilds')
        log.info(f'Connected to {len(self.users)} users')
        
        await self.cogs['Music'].start_nodes()
        log.info('Lavalink Nodes Loaded.')
        self.start_time = datetime.datetime.utcnow()

    async def setup_hook(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        self.session = aiohttp.ClientSession()

        await self.load_modules('cogs')
        await self.load_extension('jishaku')

    async def get_context(self, message: Message, *, cls=Context):
        return await super().get_context(message, cls=cls)
    
    async def on_command_error(self, ctx: Context, ex: commands.CommandError):
        if isinstance(ex, commands.errors.NotOwner):
            return await ctx.deny(f'You are not an owner of {self.user.mention}.')
        if isinstance(ex, commands.errors.CommandOnCooldown):
            return await ctx.warn(f'This command is currently on cooldown, try again in {int(ex.retry_after)}s')