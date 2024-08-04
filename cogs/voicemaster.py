import asyncio
from typing import Union
import discord

from discord import (
    VoiceChannel,
    Member
)

from discord.ext import commands
from discord.ext.commands import (
    Cog,
    group
)

from tools.ui import Interface
from tools.configuration import Emojis
from tools.heal import Heal
from tools.managers import Context

class VoiceMaster(Cog):
    def __init__(self, bot: Heal):
        self.bot = bot
        
    @group(
        name = 'voicemaster',
        description = 'Make temporary voice channels in your server!',
        invoke_without_command = True,
        aliases = [
            'vm',
            'voicem'
        ]
    )
    async def voicemaster(self, ctx: Context):
        return await ctx.send_help(ctx.command.qualified_name)
        
    @voicemaster.command(
        name = 'setup',
        description = 'Begin VoiceMaster server configuration setup'
    )
    @commands.has_permissions(manage_guild=True)
    async def voicemaster_setup(self, ctx: Context):
        if await self.bot.pool.fetchrow(
            """
            SELECT * FROM voicemaster.configuration WHERE guild_id = $1
            """,
            ctx.guild.id
        ):
            return await ctx.deny(f"**VoiceMaster** is already **setup** for this server!")
        
        category = await ctx.guild.create_category('Voice Channels')
        interface = await category.create_text_channel('interface')
        channel = await category.create_voice_channel('Join To Create')
        
        await interface.send(
            embed = discord.Embed(
                title = 'VoiceMaster Interface',
                description = 'Click the buttons below to control your voice channel.',
                url = 'https://discord.gg/baUaYS2rJ6'
            )
            .set_author(name = ctx.guild.name, icon_url = ctx.guild.icon.url if ctx.guild.icon is not None else None)
            .set_thumbnail(url = ctx.guild.icon.url if ctx.guild.icon is not None else None)
            .set_footer(text = 'The Heal Team', icon_url = self.bot.user.display_avatar.url)
            .add_field(
                name = 'Usage',
                value = (
                    f'>>> {Emojis.VOICEMASTER_LOCK} . [`Lock`](https://discord.gg/baUaYS2rJ6) the voice channel\n'
                    f'{Emojis.VOICEMASTER_UNLOCK} . [`Unlock`](https://discord.gg/baUaYS2rJ6) the voice channel\n'
                    f'{Emojis.VOICEMASTER_GHOST} . [`Ghost`](https://discord.gg/baUaYS2rJ6) the voice channel\n'
                    f'{Emojis.VOICEMASTER_REVEAL} . [`Reveal`](https://discord.gg/baUaYS2rJ6) the voice channel\n'
                    f'{Emojis.VOICEMASTER_PERSON} . [`Claim`](https://discord.gg/baUaYS2rJ6) the voice channel\n'
                    f'{Emojis.VOICEMASTER_ADD} . [`Permit`](https://discord.gg/baUaYS2rJ6) a member\n'
                    f'{Emojis.VOICEMASTER_MINUS} . [`Reject`](https://discord.gg/baUaYS2rJ6) a member\n'
                    f'{Emojis.VOICEMASTER_RENAME} . [`Rename`](https://discord.gg/baUaYS2rJ6 the voice channel\n'
                    f'{Emojis.VOICEMASTER_OWNERSHIP} . [`Transfer`](https://discord.gg/baUaYS2rJ6) the channel ownership\n'
                    f'{Emojis.VOICEMASTER_DELETE} . [`Delete`](https://discord.gg/baUaYS2rJ6) the voice channel\n'
                )
            ),
            view = Interface(self.bot)
        )
        
        await self.bot.pool.execute(
            """
            INSERT INTO voicemaster.configuration (guild_id, channel_id, interface_id, category_id)
            VALUES ($1, $2, $3, $4)
            """,
            ctx.guild.id,
            channel.id,
            interface.id,
            category.id
        )
        
        return await ctx.approve('Finished setting up the **VoiceMaster** channels. A category and two channels have been created, you can move the channels or rename them if you want.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel: 
            return
        
        if after.channel is not None and len(after.channel.members) == 0:
            await self.delete_vm_channel(after.channel, member)
        
        if before.channel is not None and len(before.channel.members) == 0:
            await self.delete_vm_channel(before.channel, member)
           
        if not (channel := await self.bot.pool.fetchval(
            """
            SELECT channel_id
            FROM voicemaster.configuration
            WHERE guild_id = $1
            """,
            member.guild.id)
        ): return
        
        if member.voice is not None and member.voice.channel.id == channel:
            return await self.create_vm_channel(member)
        
        
    async def delete_vm_channel(self, channel: VoiceChannel, member: Member):
        if not await self.bot.pool.fetchrow(
            """
            SELECT * FROM voicemaster.channels
            WHERE guild_id = $1 AND channel_id = $2
            """,
            channel.guild.id,
            channel.id
        ):
            return
        
        await self.bot.pool.execute(
            """
            DELETE FROM voicemaster.channels
            WHERE guild_id = $1 AND channel_id = $2
            """,
            channel.guild.id,
            channel.id
        )
        try:
            return await channel.delete()
        except:
            pass
    
    async def create_vm_channel(self, member: Member) -> None:
        if not (channel := await self.bot.pool.fetchrow(
            """
            SELECT * FROM voicemaster.configuration
            WHERE guild_id = $1
            """,
            member.guild.id
        )):
            return
        
        category = member.guild.get_channel(channel['category_id'])
        channel = await category.create_voice_channel(f'{member.name}\'s Channel')
        
        async with asyncio.Lock():
            await member.move_to(channel)
            await channel.set_permissions(member, connect=True, view_channel=True, manage_channels=True)
            
            await self.bot.pool.execute(
                """
                INSERT INTO voicemaster.channels (guild_id, channel_id, owner_id)
                VALUES ($1, $2, $3)
                """,
                member.guild.id,
                channel.id,
                member.id
            )
            
            await asyncio.sleep(1.2)
            if len(channel.members) == 0:
                return await self.delete_vm_channel(channel, member)
            return channel

async def setup(bot: Heal):
    await bot.add_cog(VoiceMaster(bot))