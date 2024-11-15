import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager
from typing import Callable, Optional
from ..abc import MixinMeta, CompositeMetaClass
from ..common.calc import Calculation
from ..common.pagination import Pagination

class JobEntity():
    def __init__(self):
        self.name = "Default"
        self.level = 1
        self.tier = 1
        self.income = 5000
        self.limit = 1
        self.bonuses = 0
    
class Jobs(MixinMeta):
    
    """ Jobs. """
    
    @commands.group(name="jobset")
    @commands.guild_only()
    @commands.admin()
    async def jobset(self, ctx):
        """ Job settings. """
        
    @commands.group(name="jobs")
    @commands.guild_only()
    async def jobs(self, ctx):
        """ Everything around jobs. """
    
    @jobs.command()
    @commands.guild_only()
    async def joblist(self, ctx, tier: str=None):
        """ List available jobs. """
        
        # Make it create an embed that dynamically lists all jobs in the job_category
        