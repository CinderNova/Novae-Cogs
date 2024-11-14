"""
Contains settings and commands to change them.
"""

import discord, json, random, datetime, asyncio
import redbot.core.data_manager
from discord import webhook
from discord.utils import get
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from ..abc import MixinMeta, CompositeMetaClass


class Commands(MixinMeta):
    
    @commands.group(name="claiming")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def claiming(self, ctx):
        """ The group of commands related to managing the claiming settings. """
    
    @commands.group(name="jailing")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def jailing(self, ctx):
        """ The group of commands related to managing the jail settings. """
    