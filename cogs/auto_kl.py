'''
=============================

Selfbot - Auto KL

=============================

Commands:
start_kl [channel]
stop_kl [channel]
list_kl

=============================
'''
import discord
from discord.ext import commands
import asyncio
import time
import random
import typing

# the KL instance
class KLSession:
    def __init__(self, bot, /, channel, persistent=False, start=False):
        self.is_kl: bool = False
        self.kl_channel: discord.abc.Messageable = channel
        self.next_kl: float = time.monotonic()
        self.kl_task: asyncio.Task | None = None
        self.bot = bot
        self.persistent: bool = persistent
        
        if start:
            self._start_kl()

    def _start_kl(self) -> None:
        if self.kl_task or self.is_kl:
            self._stop_kl()
        self.is_kl = True
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

    def destroy(self):
        self._stop_kl()

    async def on_ready(self):
        if (
            self.persistent
            and self.is_kl
            and self.kl_task.done()
        ):
            self._start_kl()

    async def on_message(self, message: discord.Message):
        if (not self.is_kl) or (self.kl_channel.id != message.channel.id) or (self.bot.config.mudae_id != message.author.id): return

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

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if (not self.is_kl) or (reaction.message.channel.id != self.kl_channel.id): return

        if user.id == self.bot.config.mudae_id and str(reaction.emoji) == "🛑":
            await asyncio.sleep(1.0)
            await self.kl_channel.send("$kl 12000")
            self.next_kl = time.monotonic() + random.uniform(self.bot.config.auto_kl.delay_min, self.bot.config.auto_kl.delay_max)

# manager for KL instances
class AutoKL(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
       self.kl_sessions: dict[int, KLSession] = {}
       self.initialized_instances: bool = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.initialized_instances: # initialize KLSession instance from config only once
            if (
                self.bot.config.auto_kl.auto_start.enabled
                and self.bot.config.auto_kl.auto_start.channel_id
                and (not self.kl_task or not self.kl_task.done())
            ):
                channel_id = self.bot.config.auto_kl.auto_start.channel_id
                self.kl_sessions[channel_id] = KLSession(
                    self.bot,
                    channel=self.bot.get_channel(channel),
                    persistent=True
                )
            self.initialized_instances = True
        # delegate event to KL instances
        async with asyncio.TaskGroup() as tg:
            for session in self.kl_sessions.values():
                tg.create_task(session.on_ready())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # delegate event to KL instance with same id as its channel
        if message.channel.id not in self.kl_sessions.keys(): return
        await self.kl_sessions[message.channel.id].on_message(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # delegate event to KL instance with same id as its channel
        if reaction.message.channel.id not in self.kl_sessions.keys(): return
        await self.kl_sessions[reaction.message.channel.id].on_reaction_add(reaction, user)

    @commands.command()
    async def start_kl(self, ctx: commands.Context, channel: typing.Union[discord.TextChannel, discord.Thread] = None):
        target: discord.abc.Messageable = channel if channel is not None else ctx.channel
        self.kl_sessions[target.id] = KLSession(
            self.bot,
            channel=target,
            start=True
        )
        
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def stop_kl(self, ctx: commands.Context, channel: typing.Union[discord.TextChannel, discord.Thread] = None):
        target: discord.abc.Messageable = channel if channel is not None else ctx.channel

        try:
            del self.kl_sessions[target.id]
        except:
            await ctx.reply("Channel does not have an active KL session.")
            return

        await ctx.message.add_reaction("✅")
    
    @commands.command()
    async def list_kl(self, ctx: commands.Context):
        output = [
            f"<#{session.kl_channel.id}> | ID: {session.kl_channel.id}"
            for session in self.kl_sessions.values()
        ]
        await ctx.reply("\n".join(output))

    

async def setup(bot):
    await bot.add_cog(AutoKL(bot))
