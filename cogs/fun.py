import discord
import asyncio
import random
import aiohttp
import uwuipy

from discord.ext import commands
from discord.ext.commands       import command, group, BucketType, cooldown, has_permissions

from tools.managers.context import Context, Colors
from tools.heal import Heal

class Fun(commands.Cog):
    """
    Commands for when you're bored
    """
    def __init__(self, bot: Heal):
        self.bot = bot
        self.MatchStart = {}
        self.lifes = {}

    async def get_string(self): 
        lis = await self.get_words()
        word = random.choice(lis)
        return word[:3].lower()

    async def get_words(self): 
        async with aiohttp.ClientSession() as cs: 
            async with cs.get("https://www.mit.edu/~ecprice/wordlist.100000") as r: 
                byte = await r.read()
                data = str(byte, 'utf-8')
                return data.splitlines()

    @command(
        name = "blacktea",
        description = "Play a game of blacktea."
    )
    @cooldown(1, 5, commands.BucketType.user)
    async def blacktea(self, ctx: Context): 
        try:
            if self.MatchStart[ctx.guild.id] is True: 
                return await ctx.deny("somebody in this server is already playing blacktea", mention_author=False)
        except KeyError: 
            pass 

        self.MatchStart[ctx.guild.id] = True 
        embed = discord.Embed(color=Colors.BASE_COLOR, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **10 seconds**")
        embed.add_field(name="goal", value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)  
        mes = await ctx.send(embed=embed)
        await mes.add_reaction("🍵")
        await asyncio.sleep(10)
        me = await ctx.channel.fetch_message(mes.id)
        players = [user.id async for user in me.reactions[0].users()]
        players.remove(self.bot.user.id)

        if len(players) < 2:
            self.MatchStart[ctx.guild.id] = False
            return await ctx.neutral("😦 {}, not enough players joined to start blacktea".format(ctx.author.mention), allowed_mentions=discord.AllowedMentions(users=True)) 

        while len(players) > 1: 
            for player in players: 
                strin = await self.get_string()
                await ctx.neutral(f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**", allowed_mentions=discord.AllowedMentions(users=True))
            
                def is_correct(msg): 
                    return msg.author.id == player
            
                try: 
                    message = await self.bot.wait_for('message', timeout=10, check=is_correct)
                except asyncio.TimeoutError: 
                    try: 
                        self.lifes[player] = self.lifes[player] + 1  
                        if self.lifes[player] == 3: 
                            await ctx.neutral(f" <@{player}>, you're eliminated ☠️", allowed_mentions=discord.AllowedMentions(users=True))
                            self.lifes[player] = 0
                            players.remove(player)
                            continue 
                    except KeyError:  
                        self.lifes[player] = 0   
                    await ctx.neutral(f"💥 <@{player}>, you didn't reply on time! **{2-self.lifes[player]}** lifes remaining", allowed_mentions=discord.AllowedMentions(users=True))    
                    continue
                if not strin.lower() in message.content.lower() or not message.content.lower() in await self.get_words():
                    try: 
                        self.lifes[player] = self.lifes[player] + 1  
                        if self.lifes[player] == 3: 
                            await ctx.send(f" <@{player}>, you're eliminated ☠️", allowed_mentions=discord.AllowedMentions(users=True))
                            self.lifes[player] = 0
                            players.remove(player)
                            continue 
                    except KeyError:  
                        self.lifes[player] = 0 
                    await ctx.neutral(f"💥 <@{player}>, incorrect word! **{2-self.lifes[player]}** lifes remaining", allowed_mentions=discord.AllowedMentions(users=True))
                else: 
                    await message.add_reaction("✅")  
            
        await ctx.neutral(f"👑 <@{players[0]}> won the game!", allowed_mentions=discord.AllowedMentions(users=True))
        self.lifes[players[0]] = 0
        self.MatchStart[ctx.guild.id] = False   

async def setup(bot: Heal):
    return await bot.add_cog(Fun(bot))