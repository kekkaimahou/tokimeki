'''
=============================

Selfbot - MAIN

=============================
'''
import discord
from discord.ext import commands
import asyncio
import os
import tomllib
import logging
import argparse
from pathlib import Path
from omegaconf import OmegaConf

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Run the discord bot.")

parser.add_argument("--token", type=str, help="Discord user token")
parser.add_argument("--config", type=Path, help="Config file path")

args = parser.parse_args()

current_dir = Path(__file__).parent
cogs = ["cogs." + x.stem for x in current_dir.glob("cogs/*.py") if x.is_file() and not x.stem.startswith("_")]

config_file = args.config or current_dir / "config.toml"
with config_file.open("rb") as f:
    config_data = tomllib.load(f)
default_config = OmegaConf.create()

user_config = OmegaConf.create(config_data)
config = OmegaConf.merge(default_config, user_config) # user config < default config

discord.utils.setup_logging()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!!!",
            help_command=None, # personally I don't use the help command but you can comment this out if you want
            self_bot=True, # (other users can't use your commands)
            afk=True, # this is so notifications actually work properly when the bot is running
            chunk_guilds_at_startup=False, # don't need member info
        )
        self.mudae_id = 432610292342587392 # mudae bot ID
        self.app_commands_channel_id = 1138234663668822076 # channel that has mudae commands (for using slash commands)
        self.slash_commands = []
        self.config = config
    
    async def update_cmds(channel: discord.TextChannel):
        apps = await ctx.channel.application_commands()
        self.slash_commands = [cmd for cmd in apps if isinstance(cmd, discord.SlashCommand)]

    async def setup_hook(self):
        for cog in cogs:
            await self.load_extension(cog)
            logger.debug(f"Loaded cog: {cog}")
        self.add_check(self.global_check) # probably redundant due to self_bot=True
    
    async def global_check(self, ctx):
        return ctx.author.id == ctx.bot.user.id
    
    async def on_ready(self):
        logger.info(f"""Logged in successfully! User: {self.user.name}""")
        
        app_commands_channel = self.get_channel(self.app_commands_channel_id)
        apps = await app_commands_channel.application_commands()
        self.slash_commands = [cmd for cmd in apps if isinstance(cmd, discord.SlashCommand)]


async def main():
    async with MyBot() as bot:
        await bot.start(token)

if __name__ == "__main__":
    token = args.token or os.getenv("TOKEN") or config.token # Arguments > Environment variable > Config
    if not token:
        raise ValueError(
            "Token not found. Set the token through the config file, TOKEN environment variable or command line arguments."
        )
    asyncio.run(main())
