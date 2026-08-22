'''
=============================

Selfbot - Auto KL

=============================

Commands:
start_kl
stop_kl

=============================
'''
import discord
from discord.ext import commands
import asyncio
import time
import random

class AutoKL(commands.Cog):
    def __init__(self, bot):
        self.is_kl: bool = False
        self.kl_channel: discord.Message.channel | None = None
        self.next_kl: float = time.monotonic()
        self.kl_task: asyncio.Task | None = None
        self.bot = bot

    @commands.command()
    async def start_kl(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        self._start_kl(ctx.channel)

    @commands.command()
    async def stop_kl(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        self._stop_kl()

    def _start_kl(self, channel: discord.TextChannel) -> None:
        if self.kl_task or self.is_kl:
            self._stop_kl()
        self.is_kl = True
        self.kl_channel = channel
        self.kl_task = asyncio.create_task(self._auto_kl_loop())
    
    def _stop_kl(self) -> None:
        self.is_kl = False
        if self.kl_task and not self.kl_task.done():
            self.kl_task.cancel()
            self.kl_task = None
    
    async def _auto_kl_loop(self) -> None:
        while self.is_kl:
            now = time.monotonic()
            if now >= self.next_kl and self.kl_channel:
                try:
                    await self.kl_channel.send("$kl 12000")
                    self.next_kl = now + random.uniform(self.bot.config.auto_kl.delay_min, self.bot.config.auto_kl.delay_max)
                except asyncio.exceptions.CancelledError as exc:
                    raise exc
                except Exception as exc:
                    pass
            await asyncio.sleep(1)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (not self.is_kl) or (self.kl_channel.id != message.channel.id) or (self.bot.mudae_id != message.author.id): return

        content = message.content.lower()

        if any(word in content for word in self.bot.config.auto_kl.kl_confirm):
            await self.kl_channel.send(random.choice(["y", "Y", "Yes", "yes"]))
            return

        if any(word in content for word in self.bot.config.auto_kl.many_pins):
            for _ in range(2):
                await self.kl_channel.send("$arlp")
                await asyncio.sleep(random.uniform(1.5, 2.5))
            await asyncio.sleep(random.uniform(1.0, 2.0))
            for _ in range(2):
                await self.kl_channel.send("$kl 12000")
                await asyncio.sleep(random.uniform(1.0, 1.5))
            self.next_kl = time.monotonic() + random.uniform(self.bot.config.auto_kl.delay_min, self.bot.config.auto_kl.delay_max)
            return

        if any(word in content for word in self.bot.config.auto_kl.no_kakera):
            await self.kl_channel.send(f"$givescrap {self.bot.user.mention} 5000000000")
            return

        if any(word in content for word in self.bot.config.auto_kl.givescrap_confirm) and self.bot.user.name.lower() in content:
            await self.kl_channel.send(random.choice(["y", "Y", "Yes", "yes"]))
            return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        if (not self.is_kl) or (reaction.message.channel.id != self.kl_channel.id): return

        if user.id == self.bot.mudae_id and str(reaction.emoji) == "🛑":
            await asyncio.sleep(1.0)
            await self.kl_channel.send("$kl 12000")
            self.next_kl = time.monotonic() + random.uniform(self.bot.config.auto_kl.delay_min, self.bot.config.auto_kl.delay_max)

async def setup(bot):
    await bot.add_cog(AutoKL(bot))
