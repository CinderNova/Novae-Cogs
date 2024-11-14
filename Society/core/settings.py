import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager
from typing import Callable, Optional
from ..abc import MixinMeta, CompositeMetaClass
from .common.calc import Calculation
from .common.pagination import Pagination

# levelup = self.bot.get_cog("LevelUp")
#        levelconfig = levelup.get_conf(ctx.guild)
#        profile = levelconfig.get_profile(user_id)
#        level: int = profile.level
class Settings(MixinMeta):
    
    @commands.group(name="socset")
    @commands.guild_only()
    @commands.admin()
    async def socset(self, ctx):
        """ Society's settings. """
    
    @socset.command()
    @commands.guild_only()
    @commands.admin()
    async def enable_soc(self, ctx, feature: str, choice: bool):
        """ Enable features of Society or disable them! """
        
        
        

