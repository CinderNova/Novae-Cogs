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

    
class Jobs(MixinMeta):
    
    """ Jobs. """
    
    
    
    @commands.group(name="jobset")
    @commands.guild_only()
    @commands.admin()
    async def jobset(self, ctx):
        """ Job settings. """
        
    @jobset.command()
    @commands.guild_only()
    @commands.admin()
    async def jobincome(self, ctx, option: str, income: int):
        
        """ Set the default income for a specific job, or all of them. \n 
        [options]: (any of the jobs) or all; [default_income]: a positive integer. """
        
        guild = ctx.guild
        job_list = await self.guild(guild).jobs()
        job_names = job_list.items()
        currency = await redbot.core.bank.get_currency_name(guild)
        
        
        if income <= 0:
            await ctx.send("Please enter a *trictly positive integer* number.")
            return
        
        option, option_is_in = option.lower(), False
        for index in range(0, len(job_names)):
            if option == job_names[index]["name"]:
                option_is_in = True
        
        if option != "all" and option_is_in:
            old_income = job_list[option]["income"]
            job_list[option]["income"] = income
            await ctx.send(f"You successfully changed {option}'s income from {old_income} {currency} to: \n{income} {currency}")
            await self.guild(guild).jobs.set(job_list)
        elif option == "all":
            for key in job_list:
                job_list[key]["income"] = income
                
            await self.guild(guild).jobs.set(job_list)

            await ctx.send("You have successfully changed the income of all jobs to {:,} {}.".format(income, currency))
    
    @jobset.command()
    @commands.guild_only()
    @commands.admin()
    async def jobber(self, ctx, option: str):
        
        """ Add, remove or change jobs to the config. \n 
        [options]: add, change, remove """
        
        guild = ctx.guild
        author = ctx.author
        job_list = await self.guild(guild).jobs()
        jobs_list = job_list.items()
        job_names = [job["name"] for job in jobs_list]
        currency = await redbot.core.bank.get_currency_name(guild)
        
        option = option.lower()
        
        if option not in ["add", "remove", "change"]:
            await ctx.send("Please enter a valid option. \n[Options]: Add, remove, change")
            return
        
        
        if option == "remove":
            await ctx.send(f"So you want to remove a job. Which one?")
            
            try:
                async with asyncio.timeout(150):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            messagecontent = msg.content.lower()
            if messagecontent not in job_names:
                await ctx.send("This job does not exist.")
                return
            
            job_list.pop(messagecontent)
            await self.config.guild(guild).jobs.set(job_list)
            await ctx.send("You have deleted the job {}".format(messagecontent))
        elif option == "change":
            await ctx.send(f"So you want to change a job. Which one?")
            
            try:
                async with asyncio.timeout(150):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            messageContent = msg.content.lower()
            if messageContent not in job_names:
                await ctx.send("This job does not exist.")
                return
            
            existing_job = job_list[messagecontent]
            job_Name = existing_job["name"]
            
            question = await ctx.send("Which property do you want to change?")
            
            await question.add_reaction("❎")
            await question.add_reaction("✅") # Stop
            await question.add_reaction("🔠") # Name
            await question.add_reaction("🌠") # Tier
            await question.add_reaction("⚔️") # Alignment
            await question.add_reaction("💵") # Income
            

            def check(reaction, user):
                            return (
                                user == author
                                and reaction.message.id == question.id
                                and str(reaction.emoji) in {"❎", "✅", "🔠", "🌠", "⚔️", "💵"}
                            )

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=150.0, check=check)
                except TimeoutError:
                    break
                else:
                    if str(reaction.emoji) == "✅":
                        # Close the embed
                        await question.delete()
                        return
                    elif str(reaction.emoji) == "🔠":
                        await ctx.send("What new name do you want the job to have?")
                        try:
                            async with asyncio.timeout(150):
                                new_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
                        except TimeoutError:
                            await ctx.send("You have taken too long to respond.")
                            return
                        job_list[job_Name]["name"] = new_Message.content
                        await ctx.send("You have successfully changed the name of the job to {}.".format(new_Message.content))
                        
                    elif str(reaction.emoji) == "🌠":
                        await ctx.send("What tier do you want the job to have?")
                        try:
                            async with asyncio.timeout(150):
                                new_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
                        except TimeoutError:
                            await ctx.send("You have taken too long to respond.")
                            return
                        if type(new_Message.content) != type(1):
                            await ctx.send("The tier should be a positive integer.")
                            return 
                        job_list[job_Name]["tier"] = new_Message.content
                        await ctx.send("You have successfully changed the tier of the job to Tier {}.".format(new_Message.content))
                    elif str(reaction.emoji) == "⚔️":
                        await ctx.send("What alignment do you want the job to have?")
                        try:
                            async with asyncio.timeout(150):
                                new_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
                        except TimeoutError:
                            await ctx.send("You have taken too long to respond.")
                            return
                        textCont = str(new_Message.content)
                        if textCont.lower() not in ["good", "neutral", "evil"]:
                            await ctx.send("The alignment should be either good, neutral or evil.")
                            return 
                        job_list[job_Name]["alignment"] = textCont.lower()
                        await ctx.send("You have successfully changed the alignment of the job to {}.".format(textCont.lower()))
                    elif str(reaction.emoji) == "💵":
                        await ctx.send("What income do you want the job to have?")
                        try:
                            async with asyncio.timeout(150):
                                new_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
                        except TimeoutError:
                            await ctx.send("You have taken too long to respond.")
                            return
                        if type(new_Message.content) != type(1):
                            await ctx.send("The income should be a positive integer.")
                            return 
                        job_list[job_Name]["income"] = new_Message.content
                        await ctx.send("You have successfully changed the income of the job to {:,} {}.".format(new_Message.content, currency))
                    await question.remove_reaction(reaction, user)
        elif option == "add":
            await ctx.send(f"So you want to add a job. What is its name?")
            
            try:
                async with asyncio.timeout(150):
                    name_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            cleaned = str(name_Message.content)
            cleaned = cleaned.lower()
            await ctx.send("The name of this new job is {}. What will its alignment be? (Good, Neutral, Evil)".format(cleaned))
            try:
                async with asyncio.timeout(150):
                    align_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            align = str(align_Message.content)
            if align.lower() not in ["good", "evil", "neutral"]:
                await ctx.send("Unfortunately, the entered alignment is not one of the options. Try again.")
                return
            alignment = align.lower()
            
            await ctx.send("The alignment of {} is {}. What will its income be?".format(cleaned, alignment))
            try:
                async with asyncio.timeout(150):
                    income_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            if type(int(income_Message.content)) != type(1) or int(income_Message.content) <= 0:
                await ctx.send("Unfortunately, the entered income was not a positive integer. Please try again.")
                return
            income = int(income_Message.content)
            
            await ctx.send("The alignment of {} is {}, its income will be {:,} {}. What will its tier be?".format(cleaned, alignment, income, currency))
            try:
                async with asyncio.timeout(150):
                    tier_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            if type(int(tier_Message.content)) != type(1) or int(tier_Message.content) <= 0:
                await ctx.send("Unfortunately, the entered tier was not a positive integer. Please try again.")
                return
            tier = int(tier_Message.content)
            
            job_list[cleaned] = {
                "name" : cleaned,
                "alignment" : align, 
                "income" : income,
                "tier" : tier
            }
            await ctx.send("The alignment of {} is {}, its income will be {:,} {}. The job's tier is {}. \nDo you agree?".format(cleaned, alignment, income, currency, tier))

            try:
                async with asyncio.timeout(150):
                    agree_Message = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            cnt = str(agree_Message.content)
            cnt = cnt.lower()
            if cnt in ["yes", "ye", "yas", "yup", "ya"]:
                await ctx.send("Then so be it. The job has been created.")
                await self.config.guild(guild).jobs.set(job_list)
            else:
                await ctx.send("Process has been stopped. Your answer was unclear.")
                return
    
    @commands.group(name="jobs")
    @commands.guild_only()
    async def jobs(self, ctx):
        """ Everything around jobs. """
    
    @jobs.command()
    @commands.guild_only()
    async def joblist(self, ctx, tier: str=None):
        """ List available jobs. """
        
        guild = ctx.guild
        author = ctx.author
        clr = await ctx.embed_colour()
        job_list = await self.guild(guild).jobs()
        job_names = job_list.items()
        currency = await redbot.core.bank.get_currency_name(guild)
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        all_embeds = []
        pagination_items = 8
                    
        total_items = len()
                    
        total_pages_items = total_items // pagination_items+1
        if total_items % pagination_items==0:
            if total_items <= pagination_items:
                        total_pages_items = 1
            else:
                        total_pages_items = total_items // pagination_items
        else:
                    total_pages_items = total_items // pagination_items+1
                    
        for page in range(1, total_pages_items+1):
                        
            # Log embed
            embed = discord.Embed(title="", 
                                description=f"# ** List of Jobs**\n", 
                                                    color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                        
            offset = (page-1)*pagination_items
            if abs(page*pagination_items - total_items) < pagination_items:
                if total_items <= pagination_items:
                    L = pagination_items-abs(page*pagination_items - total_items)
                else:
                    L = pagination_items-abs(page*pagination_items - total_items) + 1
                for job in job_names[offset:offset+L]:
                                job_name = job["name"]
                                alignment = job["alignment"]
                                income = job["income"]
                                tier = job["tier"]
                                embed.description += "```Job:       {}\nJob Tier:       {}\nAlignment:       {}\nIncome:       {} {}```\n".format(job_name, tier, alignment, income, currency)
            else:
                for individ in job_names[offset : offset+pagination_items]:
                    job_name = job["name"]
                    alignment = job["alignment"]
                    income = job["income"]
                    tier = job["tier"]
                    embed.description += "```Job:       {}\nJob Tier:       {}\nAlignment:       {}\nIncome:       {} {}```\n".format(job_name, tier, alignment, income, currency)
            embed.add_field(name="Date", value="{}".format(timestamp))
            embed.set_footer(text=f"Page {page} / {total_pages_items}")
                            
            all_embeds.append(embed)
        current_page = 0
        message = await ctx.send(embed=all_embeds[current_page])
        await message.add_reaction("⏪")
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("⏩")
        await message.add_reaction("✅") # Checkmark emoji

        def check(reaction, user):
            return (
                user == author
                and reaction.message.id == message.id
                and str(reaction.emoji) in {"✅", "⬅️", "➡️", "⏪", "⏩"}
            )
        while True:
            try:
                                reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0, check=check)
            except TimeoutError:
                break
            else:
                                if str(reaction.emoji) == "➡️":
                                    if current_page < total_pages_items-1:
                                        current_page += 1
                                        await message.edit(embed=all_embeds[current_page])
                                    else:
                                        current_page += 1 - total_pages_items
                                        await message.edit(embed=all_embeds[current_page])
                                elif str(reaction.emoji) == "⏩":
                                    if current_page < total_pages_items - 3:
                                        current_page += 3
                                        await message.edit(embed=all_embeds[current_page])
                                    elif total_pages_items -3<=current_page < total_pages_items:
                                        current_page += 3 - total_pages_items
                                        await message.edit(embed=all_embeds[current_page])
                                elif str(reaction.emoji) == "⏪":
                                    if current_page +1> 3:
                                        current_page -= 3
                                        await message.edit(embed=all_embeds[current_page])
                                    else:
                                        current_page = -current_page + (total_pages_items - 3)
                                        await message.edit(embed=all_embeds[current_page])
                                elif str(reaction.emoji) == "⬅️":
                                    if current_page > 0:
                                        current_page -= 1
                                        await message.edit(embed=all_embeds[current_page])
                                    else:
                                        current_page = total_pages_items - 1
                                        await message.edit(embed=all_embeds[current_page])

                                elif str(reaction.emoji) == "✅":
                                    # Close the embed
                                    await message.delete()
                                    return
                                await message.remove_reaction(reaction, user)
        
    

        
        
        
        
        
      