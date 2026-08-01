'''
=============================

Selfbot - MAIN

=============================
'''
try:
    import selfcord as discord
except ImportError:
    import discord
import asyncio
from discord.ext import commands
import os
from pathlib import Path

current_dir = Path(__file__).parent

COGS = ["cogs." + x.stem for x in current_dir.glob("*/*.py") if x.is_file()]

discord.utils.setup_logging()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!!!", 
            help_command=None, # personally I don't use the help command but you can comment this out if you want
            self_bot=True, # (other users can't use your commands)
            afk=True # this is so notifications actually work properly when the bot is running
        )
        self.mudae_id = 432610292342587392 # mudae bot ID
        self.app_commands_channel_id = 1138234663668822076 # channel that has mudae commands (for using slash commands)
        self.slash_commands = []
    
    async def setup_hook(self):
        for cog in COGS:
            await self.load_extension(cog)
            print(f"Loaded cog: {cog}")
        self.add_check(self.global_check) # probably redundant due to self_bot=True
    
    async def global_check(self, ctx):
        return ctx.author.id == ctx.bot.user.id
    
    async def on_ready(self):
        print(f"""Logged in successfully! User: {self.user.name}""")
        
        app_commands_channel = self.get_channel(self.app_commands_channel_id)
        apps = await app_commands_channel.application_commands()
        self.slash_commands = [cmd for cmd in apps if isinstance(cmd, discord.SlashCommand)]
        
        
        
        
        


async def main():
    async with MyBot() as bot:
        await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
    if not os.getenv("TOKEN"):
        raise ValueError(
            "Token not found. Set the TOKEN environment variable."
        )
    asyncio.run(main())