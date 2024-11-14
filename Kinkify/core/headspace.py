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


class Headspace(MixinMeta):
    
    @commands.group(name="headspace")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def headspace(self, ctx):
        """ The group of commands related to managing the headspace settings. """

    @headspace.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def setroles(self, ctx, option: str, suboption: str,  roles: discord.Role):
        """ Set the roles needed for kinkify. Options: [color, bdsm] and suboptions respectively: [green, yellow, red] and [dom, switch, sub, none]. """
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'multi_roles' sub-command of 'kinkify settings' command.")
            return
        
        if option.lower() == "color":
            headspace_color = await self.config.guild(guild).headspace_roles_colour()
            
            if suboption.lower() == "green":
                
                headspace_color['green'] = roles.id 
                await self.config.guild(guild).headspace_roles_colour.set(headspace_color)
                await ctx.send(f"You have successfully set the headspace color green to {roles.mention}.")
            elif suboption.lower() == "yellow":
                
                headspace_color['yellow'] = roles.id 
                await self.config.guild(guild).headspace_roles_colour.set(headspace_color)
                await ctx.send(f"You have successfully set the headspace color yellow to {roles.mention}.")
            elif suboption.lower() == "red":

                headspace_color['red'] = roles.id 
                await self.config.guild(guild).headspace_roles_colour.set(headspace_color)
                await ctx.send(f"You have successfully set the headspace color red to {roles.mention}.")
            else:
                await ctx.send("Enter a valid suboption: Either red, green or yellow.")
                return
        elif suboption.lower() == "bdsm":
            headspace_bdsm = await self.config.guild(guild).headspace_roles_bdsm()
            
            if suboption.lower() == "dom":
                
                headspace_bdsm['dominant'] = roles.id 
                await self.config.guild(guild).headspace_roles_bdsm.set(headspace_bdsm)
                await ctx.send(f"You have successfully set the headspace dominant to {roles.mention}.")
            elif suboption.lower() == "switch":
                
                headspace_bdsm['switch'] = roles.id 
                await self.config.guild(guild).headspace_roles_bdsm.set(headspace_bdsm)
                await ctx.send(f"You have successfully set the headspace switch to {roles.mention}.")
            elif suboption.lower() == "sub":
                
                headspace_bdsm['submissive'] = roles.id 
                await self.config.guild(guild).headspace_roles_bdsm.set(headspace_bdsm)
                await ctx.send(f"You have successfully set the headspace submissive to {roles.mention}.")
            elif suboption.lower() == "none":
            
                headspace_bdsm['none'] = roles.id 
                await self.config.guild(guild).headspace_roles_bdsm.set(headspace_bdsm)
                await ctx.send(f"You have successfully set the headspace none to {roles.mention}.")
            else:
                await ctx.send("You need to enter either of: [dom, switch, sub, none].")
                return
        else:
            await ctx.send("Enter a valid option from bdsm or color.")
            return
    
    @app_commands.command(description="Choose a headspace role. Giving a reason is optional.")
    @app_commands.guild_only()
    @app_commands.describe(bdsmrole="Choose the headspace role from [dominant, switch, submissive, none].", reason="Name a reason for your headspace change. Optional.")
    async def bdsmheadspace(self, interaction: discord.Interaction, bdsmrole: discord.Role, reason:str=None):
        
        """This command does as it says. You may choose your headspace (BDSM)."""
        
        # Check for the reason, make it a string. (Optional)
        if reason == None:
            reason = 'Reason not given.'

        # Set all relevant information.
        author = interaction.user
        guild = interaction.guild
        id = str(guild.id)
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        headspace_bool = await self.config.guild(guild).enable_headspace()
        headspace_logging_bool = await self.config.guild(guild).enable_headspace_logging()
        
        
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'bdsmheadspace' application command.")
            return

        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        boundaries = get(guild.channels, id = await self.config.guild(guild).boundaries())

        headspace_bdsm = await self.config.guild(guild).headspace_roles_bdsm()
        headspace_dom, headspace_switch, headspace_sub, headspace_none = headspace_bdsm['dominant'], headspace_bdsm['switch'], headspace_bdsm['submissive'], headspace_bdsm['none']
        domspace, switchspace, subspace, nonespace = get(guild.roles, id = headspace_dom), get(guild.roles, id = headspace_switch), get(guild.roles, id = headspace_sub), get(guild.roles, id = headspace_none)

        if domspace == None or switchspace == None or subspace == None or nonespace == None:
            await interaction.response.send_message(f"There are missing roles that need to be set for this feature.")
            return
        elif headspace_bool == False:
            await interaction.response.send_message(f"This feature is disabled.")
            return
        
        # Gets the relevant roles and their combinations.

        comb1=[switchspace, subspace, nonespace]
        comb2=[domspace, subspace, nonespace]
        comb3=[domspace, switchspace, nonespace]
        comb4=[domspace, switchspace, subspace]
        tempr = 0
        
        # The pain begins.
        
        if bdsmrole not in guild.roles:
            # If the role is nonsense, excludes this.
            await interaction.response.send_message(f"You need to enter a valid role.", ephemeral=True)
            return
        elif bdsmrole in author.roles:
            # If user has the role, excludes this.
            await interaction.response.send_message(f"You already have this role, {author.mention}.", ephemeral=True)
            return
        else:
            # Now. We check for multiple things: Whether the role is one we allow users to take up,
            if bdsmrole in [domspace, subspace, switchspace, nonespace]:
                # and said role determines the combination that will be checked / unassigned as well.
                if bdsmrole not in comb1:
                    assigned=f"{bdsmrole.mention} has been assigned to you. I unassigned"
                    for i in comb1:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned +f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    
                    if headspace_logging_bool:
                        await interaction.response.send_message(assigned + f" and posted notification of this change to {boundaries.mention}.", ephemeral=True)
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)    
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(bdsmrole)                           
                elif bdsmrole not in comb2:
                    # Same thing here
                    assigned=f"{bdsmrole.mention} has been assigned to you. I unassigned"
                    for i in comb2:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned + f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    if headspace_logging_bool:
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)  
                        await interaction.response.send_message(assigned + f" and posted a notification to {boundaries.mention}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(bdsmrole)       
                elif bdsmrole not in comb3:
                    # and here.
                    assigned=f"{bdsmrole.mention} has been assigned to you. I unassigned"
                    for i in comb3:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned + f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    
                    if headspace_logging_bool:
                        await interaction.response.send_message(assigned + f" and posted a notification to {boundaries.mention}.", ephemeral=True)
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)  
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(bdsmrole)
                elif bdsmrole not in comb4:
                    # Lastly, here.
                    assigned=f"{bdsmrole.mention} has been assigned to you. I unassigned"
                    for i in comb4:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned + f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    if headspace_logging_bool:
                        await interaction.response.send_message(assigned + f" and posted a notification to {boundaries.mention}.", ephemeral=True)
                    
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {bdsmrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {bdsmrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)  
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(bdsmrole)
                else:
                    # Just to make sure lol
                    await interaction.response.send_message(f"You need to enter a valid headspace role.", ephemeral=True)
            else:
                # Lastly, this one is the most important. It is the feedback for a wrong role.
                await interaction.response.send_message(f"You need to enter a valid headspace role.", ephemeral=True)
                
    @app_commands.command(description="Choose a headspace role. Giving a reason is optional.")
    @app_commands.guild_only()
    @app_commands.describe(colourrole="Choose the headspace role from [red, yellow, green].", reason="Name a reason for your headspace change. Optional.")
    async def colorheadspace(self, interaction: discord.Interaction, colourrole: discord.Role, reason:str=None):
        
        """ This command does as it says. You may choose your headspace (color). """
        
        # Check for the reason, make it a string. (Optional)
        if reason == None:
            reason = 'Reason not given.'

        # Set all relevant information.
        author = interaction.user
        guild = interaction.guild
        id = str(guild.id)
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        headspace_bool = await self.config.guild(guild).enable_headspace()
        headspace_logging_bool = await self.config.guild(guild).enable_headspace_logging()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'colorheadspace' application command.")
            return

        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        boundaries = get(guild.channels, id = await self.config.guild(guild).boundaries())

        headspace_color = await self.config.guild(guild).headspace_roles_colour()
        headspace_green, headspace_yellow, headspace_red = headspace_color['red'], headspace_color['yellow'], headspace_color['green']
        red, orange, green= get(guild.roles, id = headspace_red), get(guild.roles, id = headspace_yellow), get(guild.roles, id = headspace_green)

        if red == None or orange == None or green == None:
            await interaction.response.send_message(f"There are missing roles that need to be set for this feature.")
            return
        elif headspace_bool == False:
            await interaction.response.send_message(f"This feature is disabled.")
            return
        
    

        comb1=[orange, red]
        comb2=[green, red]
        comb3=[green, orange]
        tempr=0
        
        
        if colourrole not in guild.roles:
            # Check if the role exists.
            await interaction.response.send_message(f"You need to enter a valid role.", ephemeral=True)
            return
        elif colourrole in author.roles:
            # Check whether the user has said role already.
            await interaction.response.send_message(f"You already have this role, {author.mention}.", ephemeral=True)  
            return
        else:
            if colourrole in [red, orange, green]:
                # Check if the argument is a role within said list.
                if colourrole not in comb1:
                    
                    assigned=f"{colourrole.mention} has been assigned to you. I unassigned"
                    for i in comb1:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned +f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    if headspace_logging_bool:
                        await interaction.response.send_message(assigned + f" and posted notification of this change to {boundaries.mention}.", ephemeral=True)
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {colourrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {colourrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {colourrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {colourrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)    
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(colourrole)
                    

                elif colourrole not in comb2:
                    
                    assigned=f"{colourrole.mention} has been assigned to you. I unassigned"
                    for i in comb1:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned +f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    
                    if headspace_logging_bool:
                        await interaction.response.send_message(assigned + f" and posted notification of this change to {boundaries.mention}.", ephemeral=True)
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {colourrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {colourrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {colourrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {colourrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)    
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(colourrole)
                    

                elif colourrole not in comb3:
                    
                    assigned=f"{colourrole.mention} has been assigned to you. I unassigned"
                    for i in comb1:
                        if i in author.roles:
                            await author.remove_roles(i)
                            assigned = assigned +f" {i.mention}"
                            tempr=i.id
                    temp = get(guild.roles, id=tempr)
                    
                    
                    if headspace_logging_bool:
                        await interaction.response.send_message(assigned + f" and posted notification of this change to {boundaries.mention}.", ephemeral=True)
                        if temp == None:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role to: \n {colourrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Changed to: {colourrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)
                        else:
                            embed = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their headspace role from {temp.mention} to: \n {colourrole.mention}. \n Reason: {reason}")
                            embed_ = discord.Embed(title="Headspace Change.", description=f"{author.mention} has changed their roles: \n Previous role: {temp.mention} \n Changed to: {colourrole.mention} \n Reason: {reason}")
                            await guild.get_channel(boundaries.id).send(embed=embed)
                            await guild.get_channel(log_channel.id).send(embed=embed_)    
                    else:
                        await interaction.response.send_message(assigned + f".", ephemeral=True)
                    await author.add_roles(colourrole)
                    
                else:
                    # Just to be sure!
                    await interaction.response.send_message(f"You need to enter a valid headspace role.", ephemeral=True)
            else:
                # And to exclude roles we don't want users to get.
                await interaction.response.send_message(f"You need to enter a valid headspace role.", ephemeral=True)
    
    
    # NSFW, SFW, LITTLESPACE COMMANDS
    
    @app_commands.command(description="A command to access the NSFW-section.")
    @app_commands.guild_only()
    async def nsfwaccess(self, interaction: discord.Interaction):
        
        """This command allows you to take on the NSFW role, and gain access."""

        # Set all relevant information.
        author = interaction.user
        guild = interaction.guild
        id = str(guild.id)
        clr = 0x000000
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'nsfwaccess' application command.")
            return

        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        boundaries = get(guild.channels, id = await self.config.guild(guild).boundaries())
        little = get(guild.roles, id = await self.config.guild(guild).little_role())
        level = get(guild.roles, id = await self.config.guild(guild).level_role())
        nsfw = get(guild.roles, id = await self.config.guild(guild).nsfw_role())
        sfw = get(guild.roles, id = await self.config.guild(guild).sfw_role())
        id_role = get(guild.roles, id = await self.config.guild(guild).id_role())

        
        if little == None or sfw == None or nsfw == None or level == None or boundaries == None or log_channel == None or id_role == None:
            await interaction.response.send_message("Some roles are not set up yet.", ephemeral=True)
            return
        
        # The pain.
        if level in author.roles and id_role in author.roles:
            # User > level 5
            if nsfw in author.roles:
                # removes nsfw
                await author.remove_roles(nsfw)
                
                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has lost {nsfw.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has lost {nsfw.mention}", color=clr)

                
                await interaction.response.send_message(f"Your wish is my command. You have lost {nsfw.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
            else:
                # adds nsfw, removes littlespace if need be.
                if little in author.roles:
                    await author.remove_roles(little)
                    yes = 0
                elif sfw in author.roles:
                    await author.remove_roles(sfw)
                    yes = 1
                yes = 2
                await author.add_roles(nsfw)
                
                if yes == 0:
                    embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention}, and lost {little.mention}.", color=clr)
                    embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention}, and lost {little.mention}.", color=clr)
                    await interaction.response.send_message(f"Your wish is my command. You have gained {nsfw.mention} and lost {little.mention}.", ephemeral=True)
                elif yes == 1:
                    embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention} and lost {sfw.mention}.", color=clr)
                    embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention} and lost {sfw.mention}.", color=clr)
                    await interaction.response.send_message(f"Your wish is my command. You have gained {nsfw.mention} and lost {sfw.mention}.", ephemeral=True)
                elif yes == 2:
                    embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention}.", color=clr)
                    embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention}", color=clr)
                    await interaction.response.send_message(f"Your wish is my command. You have gained {nsfw.mention}.", ephemeral=True)
                

                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
        elif level in author.roles and id_role not in author.roles:
            await interaction.response.send_message(f"You need to be age (ID) verified to get {nsfw.mention}.", ephemeral=True)
        elif level not in author.roles and id_role in author.roles:
            await interaction.response.send_message(f"You need to have the role {level.mention} to get {nsfw.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You need to have the role {level.mention} to get {nsfw.mention}.", ephemeral=True)
    
    
    @app_commands.command(description="A command to get into Littlespace, if you choose so.")
    @app_commands.guild_only()
    async def getlittlespace(self, interaction: discord.Interaction):
        
        """This command allows you to take on a "Little" role."""

        # Set all relevant information.
        author = interaction.user
        guild = interaction.guild
        id = str(guild.id)
        clr = 0x000000
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'nsfwaccess' application command.")
            return

        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        boundaries = get(guild.channels, id = await self.config.guild(guild).boundaries())
        little = get(guild.roles, id = await self.config.guild(guild).little_role())
        level = get(guild.roles, id = await self.config.guild(guild).level_role())
        nsfw = get(guild.roles, id = await self.config.guild(guild).nsfw_role())
        sfw = get(guild.roles, id = await self.config.guild(guild).sfw_role())
        rolelist = [level, little, nsfw, sfw]
        
        if little == None or sfw == None or nsfw == None or level == None or boundaries == None or log_channel == None:
            await interaction.response.send_message("Some roles are not set up yet.", ephemeral=True)
            return

        
        # The pain.
        if little not in author.roles:
            # If they don't have little, 
            if nsfw in author.roles:
                # and DO have nsfw, remove nsfw and add little,
                await author.remove_roles(nsfw)
                await author.add_roles(little)

                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {little.mention} and lost {nsfw.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {little.mention} and lost {nsfw.mention}.", color=clr)
                
                await interaction.response.send_message(f"Your wish is my command. You have gained {little.mention} and lost {nsfw.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
            else:
                # and don't have nsfw, add little,
                await author.add_roles(little)
                
                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {little.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {little.mention}.", color=clr)
                
                await interaction.response.send_message(f"Your wish is my command. You have gained {little.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
        else:
            # If they have little,
            if level in author.roles:
                # and are > level 5, remove little and add nsfw,
                await author.remove_roles(little)
                await author.add_roles(nsfw)
                
                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention} and is no longer in {little.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {nsfw.mention} and is no longer in {little.mention}.", color=clr)
                
                await interaction.response.send_message(f"Your wish is my command. You have lost {little.mention} and gained {nsfw.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
            else:
                # and are < level 5, remove little.
                await author.remove_roles(little)
                
                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} is no longer in {little.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} is no longer in {little.mention}.", color=clr)

                
                await interaction.response.send_message(f"Your wish is my command. You have lost {little.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
    
    
    @app_commands.command(description="A command to access the NSFW-section.")
    @app_commands.guild_only()
    async def sfw(self, interaction: discord.Interaction):
        
        """ This command allows you to take on the SFW role. """

        # Set all relevant information.
        author = interaction.user
        guild = interaction.guild
        id = str(guild.id)
        clr = 0x000000
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'nsfwaccess' application command.")
            return

        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        boundaries = get(guild.channels, id = await self.config.guild(guild).boundaries())
        little = get(guild.roles, id = await self.config.guild(guild).little_role())
        level = get(guild.roles, id = await self.config.guild(guild).level_role())
        nsfw = get(guild.roles, id = await self.config.guild(guild).nsfw_role())
        sfw = get(guild.roles, id = await self.config.guild(guild).sfw_role())
        rolelist = [level, little, nsfw, sfw]
        
        if little == None or sfw == None or nsfw == None or level == None or boundaries == None or log_channel == None:
            await interaction.response.send_message("Some roles are not set up yet.", ephemeral=True)
            return
        
        # The pain.
        if level in author.roles:
            # User > level 5
            if sfw in author.roles:
                # removes sfw
                await author.remove_roles(sfw)
                
                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has lost {sfw.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has lost {sfw.mention}", color=clr)

                
                await interaction.response.send_message(f"Your wish is my command. You have lost {sfw.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
            else:
                # adds sfw, removes nsfw
                await author.add_roles(sfw)
                await author.remove_roles(nsfw)
                
                embed = discord.Embed(title="Headspace Change.", description=f"{interaction.user.mention} now has {sfw.mention} and lost {nsfw.mention}.", color=clr)
                embed_ = discord.Embed(title="Log: Headspace Change.", description=f"{interaction.user.mention} now has {sfw.mention} and lost {nsfw.mention}.", color=clr)


                
                await interaction.response.send_message(f"Your wish is my command. You have gained {sfw.mention}, and lost {nsfw.mention}.", ephemeral=True)
                await guild.get_channel(boundaries.id).send(embed=embed)
                await guild.get_channel(log_channel.id).send(embed=embed_)
    
    