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
        else:
            await ctx.send("You need to enter an existing feature, or you do not have the necessary permissions.")
    
    @socset.command()
    @commands.guild_only()
    @commands.admin()
    async def incomeset(self, ctx, option: str, default_income: int):
        
        """ Set the default income for a specific job, or all of them. \n 
        [options]: (any of the jobs) or all; [default_income]: a positive integer. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        job_list = await self.guild(guild).jobs()
        job_names = job_list.items()
        currency = await redbot.core.bank.get_currency_name(guild)
        
        
        if default_income <= 0:
            await ctx.send("Please enter a *trictly positive integer* number.")
            return
        
        option, option_is_in = option.lower(), False
        for index in range(0, len(job_names)):
            if option == job_names[index][0]:
                option_is_in = True
        
        if option != "all" and option_is_in:
            old_income = job_list[option][2]
            job_list[option][2] = default_income
            await ctx.send(f"You successfully changed {option}'s income from {old_income} {currency} to: \n{default_income} {currency}")
            await self.guild(guild).jobs.set(job_list)
        elif option == "all":
            name_list_order, old_income_list_order = [], []
            for key in job_list:
                name_list_order.append(job_list[key][0])
                old_income_list_order.append(job_list[key][2])
                job_list[key][2] = default_income
                
            await self.guild(guild).jobs.set(job_list)
            
            log_message = "The following jobs have had their default income changed from \n"
            for i in range(0, len(name_list_order)):
                log_message += f"{name_list_order[i]} {currency}\n"
            log_message += f"to {default_income} {currency}."
            await ctx.send(log_message)
        
        
        
        'default_income' : 5000,
            'max_bet' : 50000,
            
            'users' : {},
            
            'jobs' : {
                    "queen" : ["queen", "good", 5000, 1],
                    "king" : ["king", "good", 5000, 1],
                    "knight" : ["knight", "good", 5000, 1],
                    "jester" : ["jester", "neutral", 5000, 2],
                    "pawn" : ["pawn", "neutral", 5000, 2],
                    "servant" : ["servant", "neutral", 5000, 2],
                    "mafioso" : ["mafioso", "bad", 5000, 3],
                    "prostitute" : ["prostitute", "bad", 5000, 3],
                    "bishop" : ["bishop", "bad", 5000, 3]
                },
            
            'job_bonuses' : {
                "first" : 1.00,
                "second" : 1.25,
                "third" : 1.375},