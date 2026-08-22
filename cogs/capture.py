'''
=============================

Selfbot - Capture messages

=============================

Commands:
start_capture
stop_capture

=============================
'''
import discord
from discord.ext import commands
import asyncio
import io

class Capture(commands.Cog):
    def __init__(self, bot):
        self.is_capturing: bool = False
        self.capture_channel: discord.Message.channel | None = None
        self.capture_content: str = ""
        self.bot = bot
    
    @commands.command()
    async def start_capture(self, ctx: commands.Context):
        await ctx.message.delete()
        self.is_capturing = True
        self.capture_channel = ctx.channel
    
    @commands.command()
    async def stop_capture(self, ctx: commands.Context):
        await ctx.message.delete()
        self.is_capturing = False
        self.capture_channel = None
        if self.capture_content:
            capture_file = io.BytesIO(self.capture_content.encode("utf-8"))
            await ctx.send(file=discord.File(capture_file, filename="capture.txt"))
            self.capture_content = ""
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.is_capturing: return
        if message.channel.id != self.capture_channel.id: return
        if message.author.id == self.bot.user.id: return
        self.capture_content += message.content + "\n"

    
async def setup(bot):
    await bot.add_cog(Capture(bot))