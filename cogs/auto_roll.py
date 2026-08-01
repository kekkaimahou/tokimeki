'''
=============================

Selfbot - Auto Roll & Auto Click Roll Buttons

=============================

Commands:
start_roll <roulette>
stop_roll
Example:
start_roll $wa - starts rolling $wa with text commands
start_roll /wa - starts rolling /wa with slash commands
If no slash command is found, defaults to $wa.

=============================
'''
import discord
from discord.ext import commands
import asyncio
import time
import random
import re

delay_min = 2.0
delay_max = 3.0
delay_min_slash = 3.0
delay_max_slash = 4.2
auto_click_buttons = r"(?:kakera(?:P)|sp.)2?"

class auto_roll(commands.Cog):
    def __init__(self, bot):
        self.is_roll: bool = False
        self.roll_channel: discord.Message.channel | None = None
        self.next_roll: float = time.monotonic()
        self.roll_task: asyncio.Task | None = None
        self.roulette: str | discord.Interaction | None = None
        self.bot = bot

    @commands.command()
    async def start_roll(self, ctx, roulette: str = "$wa"):
        await ctx.message.delete()
        match roulette[0]:
            case "$":
                self.roulette = roulette
            case "/":
                try:
                    self.roulette = [cmd for cmd in self.bot.slash_commands if cmd.name == roulette.replace("/", "")][0]
                except IndexError:
                    self.roulette = "$wa"
            case _:
                self.roulette = "$" + roulette
        self._start_roll(ctx.channel)

    @commands.command()
    async def stop_roll(self, ctx):
        await ctx.message.delete()
        self._stop_roll()

    def _start_roll(self, channel):
        if self.roll_task or self.is_roll:
            self._stop_roll()
        self.is_roll = True
        self.roll_channel = channel
        self.roll_task = asyncio.create_task(self._auto_roll_loop())
    
    def _stop_roll(self):
        self.is_roll = False
        if self.roll_task and not self.roll_task.done():
            self.roll_task.cancel()
            self.roll_task = None
    
    def check_message_components(self, message: discord.Message, regex_match):
        if not message.components: return []
        return [button for button in message.components[0].children if re.search(regex_match, button.emoji.name) or button.style != discord.ButtonStyle.secondary]
        
    async def _auto_roll_loop(self):
        while self.is_roll:
            now = time.monotonic()
            if now >= self.next_roll and self.roll_channel:
                try:
                    if isinstance(self.roulette, str):
                        await self.roll_channel.send(f"{self.roulette}")
                        self.next_roll = now + random.uniform(delay_min, delay_max)
                    elif isinstance(self.roulette, discord.SlashCommand):
                        await self.roulette(self.roll_channel)
                        self.next_roll = now + random.uniform(delay_min_slash, delay_max_slash)
                    else:
                        return
                except asyncio.exceptions.CancelledError as exc:
                    raise exc
                except Exception as exc:
                    pass
            await asyncio.sleep(0.5)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (not self.is_roll) or (self.roll_channel.id != message.channel.id) or (self.bot.mudae_id != message.author.id): return
        click_queue = self.check_message_components(message, auto_click_buttons)
        if click_queue:
            for button in click_queue:
                await button.click()
                await asyncio.sleep(2)
            
        


async def setup(bot):
    await bot.add_cog(auto_roll(bot))