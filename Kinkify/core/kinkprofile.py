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
from ..abc import MixinMeta

async def staff_check(self, ctx, member: discord.Member) -> bool:
        """" Check if a user has a mod or staff role. """
        
        guild = ctx.guild

        
        if member not in guild.members:
            return False
        
        if redbot.core.utils.mod.is_mod_or_superior(self, member):
            return True
        else:
            return False

def element_check(search_through, property: str, search_property):
    is_in = False
    sought_element = None
    
    if type(search_through) == dict:
        for key, value in search_through.items():
            if str(value[property]).lower() == str(search_property).lower():
                is_in = True
                sought_element = search_through[key]
    elif type(search_through) == list:
        for item in search_through:
            if type(item) == dict:

                if str(item[property]).lower() == str(search_property).lower():
                    is_in = True
                    sought_element = item

            elif type(item) != list or type(item) != dict:
                if str(item).lower() == str(search_property).lower():
                    is_in = True
                    sought_element = item
            
    return [is_in, sought_element]

async def manager_check(self, ctx, member:discord.Member) -> bool:
        
    guild = ctx.guild

    if member not in guild.members:
        return False
    
    managers = await self.config.guild(guild).manager_roles()
    manager_roles = managers['roles']
    manager_users = managers['members']
    
    is_in = False
    
    if manager_users:
        
        if manager_roles:
            for roles in member.roles:
                if roles.id in manager_roles or member.id in manager_users:
                    is_in = True
        else:
            if member.id in manager_users:
                is_in = True
    else:
        if manager_roles:
            for roles in member.roles:
                if roles.id in manager_roles:
                    is_in = True
    
    return is_in

async def immunity_check(self,ctx,member:discord.Member, gag: bool, jail: bool):
    guild = ctx.guild
    
    if member not in guild.members:
        return False
    
    immunity = await self.config.guild(guild).immunity()
    jail_immunity = await self.config.guild(guild).jail_immunity()
    gag_immunity = await self.config.guild(guild).gag_immunity()
    
    jail_bool = await self.config.guild(guild).enable_staff_jail_immunity()
    gag_bool = await self.config.guild(guild).enable_staff_gag_immunity()
    
    immune_roles = immunity['roles']
    immune_members = immunity['members']
    jail_immune_roles = jail_immunity['roles']
    jail_immune_members = jail_immunity['members']
    gag_immune_roles = gag_immunity['roles']
    gag_immune_members = gag_immunity['members']
    
    is_immune = False
    is_immune_gag = False
    is_immune_jail = False
    
    if jail_bool and jail:
        if jail_immune_members:
            if jail_immune_roles:
                for roles in member.roles:
                    if roles.id in jail_immune_roles or member.id in jail_immune_members:
                        is_immune_jail = True
            else:
                if member.id in jail_immune_members:
                    is_immune_jail = True
        else:
            if jail_immune_roles:
                for roles in member.roles:
                    if roles.id in jail_immune_roles:
                        is_immune_jail = True
    
    if gag_bool and gag:
        if gag_immune_members:
            if gag_immune_roles:
                for roles in member.roles:
                    if roles.id in gag_immune_roles or member.id in gag_immune_members:
                        is_immune_gag = True
            else:
                if member.id in gag_immune_members:
                    is_immune_gag = True
        else:
            if gag_immune_roles:
                for roles in member.roles:
                    if roles.id in gag_immune_roles:
                        is_immune_gag = True
        

    if immune_members:
            if immune_roles:
                for roles in member.roles:
                    if roles.id in immune_roles or member.id in immune_members:
                        is_immune = True
            else:
                if member.id in immune_members:
                    is_immune = True
    else:
            if immune_roles:
                for roles in member.roles:
                    if roles.id in immune_roles:
                        is_immune = True
    
    return is_immune, is_immune_jail, is_immune_gag
     
async def preference_check(self, ctx, member: discord.Member, partner: discord.Member):
    
    """ Checks whether or not a member is a partner. """
    
    guild = ctx.guild
    author = ctx.message.author
    can_do =  False
        
    if member not in guild.members:
        return can_do
        
        
    profiles = await self.config.guild(guild).user_profiles()

    user = {
            "member_name" : member.name,
            "member_id" : member.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        
    for key in profiles:
            if profiles[key]["member_id"] == member.id:
                user = profiles[key]
        
    if user["general_preference"] == "nobody":
        return can_do
    elif user["general_preference"] == "owner":
        if user["claims"] == {}:
            return can_do
        else:
            for key in user["claims"]:
                if user["claims"][key]['partner_id'] == author.id:
                    can_do = True
            return can_do
    elif user["general_preference"] == "ask":
        can_do = "ask"
        return can_do
    elif user["general_preference"] == "everyone":
        can_do = True
        return can_do
    
async def userprofile(self, member: discord.Member):
    guild = member.guild
    user = {
            "member_name" : member.name,
            "member_id" : member.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "nobody",
            "gag_preference" : "nobody",
            "general_preference" : "nobody",
            "roles" : None,
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
    return user


class Kinkprofile(MixinMeta):
    
    @commands.group(name="mykinkprofile")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def mykinkprofile(self, ctx):
        """ The group of commands related to managing the kink profile. """
    
    
    # Kink Profile commands
    
    @mykinkprofile.command()
    @commands.guild_only()
    async def preferences(self, ctx, option: str, preference: str):
        
        """ Set your preference for being jailed or gagged. \n Options: [gag, jail, general] \nPreferences: [everyone, owner, ask, nobody]"""

        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'preferences' command.")
            return
        
        if preference.lower() not in ["everyone", "owner", "ask", "nobody"]:
            await ctx.send("You need to enter a valid option: [everyone, owner, ask, nobody].")
            return
        profiles = await self.config.guild(guild).user_profiles()
        user = {
            "member_name" : author.name,
            "member_id" : author.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        for key in profiles:
            if profiles[key]["member_id"] == author.id:
                user = profiles[key]
        
        
        
        if option.lower() == "gag":
            user["gag_preference"] = preference.lower()
        elif option.lower() == "jail":
            user["jail_preference"] = preference.lower()
        elif option.lower() == "general":
            user["general_preference"] = preference.lower()
        else:
            await ctx.send("You need to enter a valid option, either jail or gag.")
            return
        
        profiles[author.id] = user

        await self.config.guild(guild).user_profiles.set(profiles)
        await ctx.send(f"You have successfully set your {option.lower()} preference to {preference.lower()}.")
    
    @mykinkprofile.command()
    @commands.guild_only()
    async def colorchange(self, ctx, option: str):
        
        """ Set the color of the embed sent when you view your profile. \n Enter a hexcode (e.g. #fffff), or enter it as 0x + the letters / numbers after the #. """

        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'colorchange' command.")
            return
        
        option = option.lower()
        
        if not option.startswith("#") and not option.startswith("0x") or len(option) > 8:
            await ctx.send("You need to enter a valid colour code.")
            return

        
        profiles = await self.config.guild(guild).user_profiles()

        user = {
            "member_name" : author.name,
            "member_id" : author.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        for key in profiles:
            if profiles[key]["member_id"] == author.id:
                user = profiles[key]
        
        user["color"] = option
        
        profiles[author.id] = user

        await self.config.guild(guild).user_profiles.set(profiles)
        await ctx.send(f"You have successfully set your profile's embed color to {option}.")
    
    @mykinkprofile.command()
    @commands.guild_only()
    async def safewordchange(self, ctx, option: str):
        
        """ Set your safeword! """

        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'safewordchange' command.")
            return
        
        option = option.lower()
        
        profiles = await self.config.guild(guild).user_profiles()

        user = {
            "member_name" : author.name,
            "member_id" : author.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        for key in profiles:
            if profiles[key]["member_id"] == author.id:
                user = profiles[key]
        
        user["safeword"] = option
        
        profiles[author.id] = user

        await self.config.guild(guild).user_profiles.set(profiles)
        await ctx.send(f"You have successfully set your safeword to {option}.")
    
    @commands.command()
    @commands.guild_only()
    async def strike(self, ctx, member: discord.Member, quantity: int=None, reason: str=None):
        
        """ Strike a member 'quantity' times (e.g. 3 times) with a reason. Entering quantity and reason is optional. \n Default: quantity = 1. """

        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'strike' command.")
            return
        
        if member not in guild.members:
            await ctx.send("You cannot strike a member not part of this community.")
            return
        
        if member == author:
            await ctx.send("You cannot strike yourself.")
            return
        
        if reason == None:
            reason = "Reason not given."
        elif quantity == None:
            quantity = 1
        
        profiles = await self.config.guild(guild).user_profiles()

        user = {
            "member_name" : author.name,
            "member_id" : author.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        
        for key in profiles:
            if profiles[key]["member_id"] == member.id:
                user = profiles[key]
        
        preference = preference_check(self, ctx, member, author)
        
        if preference == False:
            await ctx.send("You cannot strike this member.")
        elif preference == True:
            user["strikes"] += quantity
        elif preference == "ask":
            await ctx.send(f"Do you consent to receiving a strike from {author.mention}, {member.mention}?")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == member)
            except TimeoutError:
                await ctx.send(f"{member.name} has taken too long to respond. Strike denied.")
                return
            if msg.content != None:
                if [word for word in msg.content.lower() if word in ["yes", "yay", "ya", "yep"]] != []:
                    user["strikes"] += quantity
                    
                elif "no" in msg.content.lower():
                    await ctx.send("The strike has been denied.")
                    return
                else:
                    await ctx.send("There has been an error.")
                    return
            else:
                await ctx.send("My apologies, however, I have encountered an error.")
                return
        if quantity != 1:
            await ctx.send(f"{member.mention} has received {quantity} strikes from {author.mention}.")
        else:
            await ctx.send(f"{member.mention} has received {quantity} strike from {author.mention}.")                    

        profiles[author.id] = user
        await self.config.guild(guild).user_profiles.set(profiles)
    
    @commands.command()
    @commands.guild_only()
    async def badwords(self, ctx, member: discord.Member, option: str, *, badwords: str):
        
        """ Add bad words to the blacklist of a member. \n Only if you are their owner. \nOptions: [add, remove]"""

        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'strike' command.")
            return
        
        if member not in guild.members:
            await ctx.send("You cannot strike a member not part of this community.")
            return

        if member == author:
            await ctx.send("You cannot blacklist words for yourself.")
            return
        option = option.lower()
        if option not in ["add", "remove"]:
            await ctx.send("You need to enter a proper option.")
            return
        
        profiles = await self.config.guild(guild).user_profiles()

        user = {
            "member_name" : author.name,
            "member_id" : author.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        
        for key in profiles:
            if profiles[key]["member_id"] == member.id:
                user = profiles[key]
        
        preference = user["general_preference"]
        claims = user["claims"]
        if preference == "ask" or preference == "nobody" or preference == "everyone":
            await ctx.send("You cannot blacklist words for this member.")
            return
        elif claims == {}:
            await ctx.send("You cannot blacklist words for this member.")
            return
        
        is_domme = False
        
        for key in claims:
            if claims[key]["partner_id"] == author.id:
                is_domme = True
        
        if is_domme == False: 
            await ctx.send("You cannot blacklist words for this member.")
        
        else:
            if option == "add":
                if badwords not in user["bad_words"]:
                    user["bad_words"].append(badwords)
                else:
                    await ctx.send("Already present within the blacklist.")
                    return
            elif option == "remove":
                if badwords in user["bad_words"]:
                    user["bad_words"].remove(badwords)
                else:
                    await ctx.send("Not found in the blacklist.")
                    return
        
        profiles[author.id] = user
        await self.config.guild(guild).user_profiles.set(profiles)
    
    
    
    @commands.command()
    @commands.guild_only()
    async def kinkprofile(self, ctx, member: discord.Member=None):
        
        """ See your own kinkify profile. """

        guild = ctx.guild
        author = ctx.message.author
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'kinkprofile' command.")
            return
        
        profiles = await self.config.guild(guild).user_profiles()
        existing = False
        user = {
            "member_name" : author.name,
            "member_id" : author.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        
        
        if member == None:
            for key in profiles:
                if profiles[key]["member_id"] == author.id:
                    existing = True
                    user = profiles[key]
                    
            
                    
            if existing == False:
                profiles[author.id] = user
                await self.config.guild(guild).user_profiles.set(profiles)       
            color = str(user["color"])
            clr = discord.Colour.from_str(color)
            claims = ""
            u_claims = user['claims']
            if u_claims == {}:
                claims += "None."
            else:
                for key in u_claims:
                    claims += f"Member Name: {u_claims[key]['member_name']}, Partner Name: {u_claims[key]['partner_name']} \n"
            bad_words = ""
            if user['bad_words'] == []:
                bad_words = "None."
            else:
                for word in user['bad_words']:
                    bad_words += word.lower()
            
            txt = f"**Member:** {user['member_name']} ({user['member_id']}) \n# Preferences: \n**General**: {user['general_preference']} \n**Jail**: {user['jail_preference']} \n**Gag**: {user['gag_preference']} \n\n# Claims: \n{claims} \n\n# Bad Words: \n{bad_words}"
            
            embed = discord.Embed(title=f"Kink Profile", 
                                description=txt, 
                                color=clr)
            embed.add_field(name="Status", value="Jail: {} \nGag: {}".format(str(user['jail_status']), str(user['gag_status'])))
            embed.add_field(name="Safeword", value=f"{user['safeword']}")
            embed.add_field(name="Strikes", value=f"{user['strikes']}")
            embed.add_field(name="Last Gag Type", value=f"{user['gag_type']}")
            
            embed.set_author(name=" - Kink Profile of {} - ".format(author.name), icon_url=author.display_avatar.url)
            embed.set_footer(text=f"Date -    {timestamp}")
            
            await ctx.send(embed=embed)
        elif member != None:
            for key in profiles:
                if profiles[key]["member_id"] == member.id:
                    existing = True
                    user = profiles[key]
                    
            
                    
            if existing == False:
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles.set(profiles)
                        
            color = str(user["color"])
            clr = discord.Colour.from_str(color)
            claims = ""
            u_claims = user['claims']
            if u_claims == {}:
                claims += "None."
            else:
                for key in u_claims:
                    claims += f"Member Name: {u_claims[key]['member_name']}, Partner Name: {u_claims[key]['partner_name']} \n"
            bad_words = ""
            if user['bad_words'] == []:
                bad_words = "None."
            else:
                for word in user['bad_words']:
                    bad_words += word.lower()
            
            txt = f"**Member:** {user['member_name']} ({user['member_id']}) \n# Preferences: \n**General**: {user['general_preference']} \n**Jail**: {user['jail_preference']} \n**Gag**: {user['gag_preference']} \n\n# Claims: \n{claims} \n\n# Bad Words: \n{bad_words}"
            
            embed = discord.Embed(title=f"Kink Profile", 
                                description=txt, 
                                color=clr)
            embed.add_field(name="Status", value="Jail: {} \nGag: {}".format(str(user['jail_status']), str(user['gag_status'])))
            embed.add_field(name="Safeword", value=f"{user['safeword']}")
            embed.add_field(name="Strikes", value=f"{user['strikes']}")
            embed.add_field(name="Last Gag Type", value=f"{user['gag_type']}")
            
            embed.set_author(name=" - Kink Profile of {} - ".format(member.name), icon_url=member.display_avatar.url)
            embed.set_footer(text=f"Date -    {timestamp}")
            
            await ctx.send(embed=embed)
                
                