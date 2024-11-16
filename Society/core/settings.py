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
    async def enable(self, ctx, feature: str, choice: str):
        """ Enable features of Society or disable them! """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()

        if feature.lower() == "debug" and (await Red.is_owner(self.bot, author)):
            # Enable or disable debugging. (Bot-owner only)
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_debug.set(True)
                await ctx.send("You have enabled debugging.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_debug.set(False)
                await ctx.send("You have disabled debugging.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
                
        elif feature.lower() == "gambling":
            # Enable or disable gambling.
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_gambling.set(True)
                await ctx.send("You have enabled gambling.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_gambling.set(False)
                await ctx.send("You have disabled gambling.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "bonuses":
            # Enable or disable bonuses.
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_bonuses.set(True)
                await ctx.send("You have enabled bonuses.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_bonuses.set(False)
                await ctx.send("You have disabled bonuses.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "jobs":
            # Enable or disable jobs.
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_jobs.set(True)
                await ctx.send("You have enabled jobs.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_jobs.set(False)
                await ctx.send("You have disabled jobs.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
    	
        elif feature.lower() == "marriage":
            # Enable or disable marriage.
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_marriage.set(True)
                await ctx.send("You have enabled marriage.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_marriage.set(False)
                await ctx.send("You have disabled marriage.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")

        elif feature.lower() == "shop":
            # Enable or disable shop.
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_shop.set(True)
                await ctx.send("You have enabled shop.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_shop.set(False)
                await ctx.send("You have disabled shop.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        elif feature.lower() == "event":
            # Enable or disable shop.
            if bool.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_event.set(True)
                await ctx.send("You have enabled event mode.")
            elif bool.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_event.set(False)
                await ctx.send("You have disabled event mode.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        else:
            await ctx.send("You need to enter an existing feature, or you do not have the necessary permissions.")
    
    @socset.command()
    @commands.guild_only()
    @commands.admin()
    async def set_income(self, ctx, income: int):
        
        """ Set the default income for a specific job, or all of them. \n 
        [options]: (any of the jobs) or all; [default_income]: a positive integer. """
        
        guild = ctx.guild
        currency = await redbot.core.bank.get_currency_name(guild)
        
        
        if income <= 0:
            await ctx.send("Please enter a *strictly positive integer* number.")
            return
        
        await self.config.guild(guild).default_income.set(income)
        await ctx.send("You have successfully set the default income to {:,} {}.".format())
    
    @socset.command()
    @commands.guild_only()
    @commands.admin()
    async def max_bet(self, ctx, bet: int):
        
        """ Set the max amount of money that can be bet. \n 
        [bet]: a positive integer. """
        
        guild = ctx.guild
        currency = await redbot.core.bank.get_currency_name(guild)
        
        
        if bet <= 0:
            await ctx.send("Please enter a *strictly positive integer* number.")
            return
        
        await self.config.guild(guild).max_bet.set(bet)
        await ctx.send("You have successfully set the max bet amount to {:,} {}.".format()) 

