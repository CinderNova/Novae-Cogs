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


class Settings(MixinMeta):
    
    @commands.group(name="kinkify")
    @commands.guild_only()
    @commands.admin()
    async def kinkset(self, ctx):
        """ The group of commands related to managing the kinkify cog. """
    
    @kinkset.group(name="settings")
    @commands.guild_only()
    @commands.admin()
    async def settings(self, ctx):
        """ The group of commands related to managing kinkify settings. """
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def channels(self, ctx, option: str, channel: discord.TextChannel):
        """ Set the channels needed for overseer. Possible options are: [modlog, log, staff, jail_log, task, jail, claim, boundaries]."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'channels' sub-command of 'kinkify settings' command.")
            return
        
        # Determine all the possible channel calls.
        if option.lower() == "modlog":
            # The option is the channel you want to set.
            await self.config.guild(guild).modlog_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the mod log to {channel.mention}, {author.name}.")

        elif option.lower() == "log":
            # The option is the channel you want to set.
            await self.config.guild(guild).log_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the log channel to {channel.mention}, {author.name}.")
            
        elif option.lower() == "jail_log":
            # The option is the channel you want to set.
            await self.config.guild(guild).jail_log_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the jail log to {channel.mention}, {author.name}.")

        elif option.lower() == "staff":
            # The option is the channel you want to set.
            await self.config.guild(guild).staff_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the staff channel to {channel.mention}, {author.name}.")

        elif option.lower() == "task":
            # The option is the channel you want to set.
            await self.config.guild(guild).task_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the task channel to {channel.mention}, {author.name}.")

        elif option.lower() == "jail":
            # The option is the channel you want to set.
            await self.config.guild(guild).jail_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the jail channel to {channel.mention}, {author.name}.")

        elif option.lower() == "claim":
            # The option is the channel you want to set.
            await self.config.guild(guild).claim_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the claim channel to {channel.mention}, {author.name}.")

        elif option.lower() == "boundaries":
            # The option is the channel you want to set.
            await self.config.guild(guild).boundaries.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the boundaries channel to {channel.mention}, {author.name}.")
        
        else:
            await ctx.send("You need to enter a valid option and / or text channel for this to work.")
            return
        
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def roles(self, ctx, option: str, role: discord.Role):
        """ Set the roles needed for kinkify. Options are: [nsfw, sfw, little, staff, jail, claimed, gagged, level]."""
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'roles' sub-command of 'kinkify settings' command.")
            return
        
        # Determine all possible roles calls.
        if option.lower() == "nsfw":
            # Set the respective role..
            await self.config.guild(guild).nsfw_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the NSFW role to {role.mention}, {author.name}.")

        elif option.lower() == "sfw":
            # Set the respective role..
            await self.config.guild(guild).sfw_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the SFW role to {role.mention}, {author.name}.")
        
        elif option.lower() == "little":
            # Set the respective role..
            await self.config.guild(guild).little_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the little role to {role.mention}, {author.name}.")
        
        elif option.lower() == "level":
            # Set the respective role..
            await self.config.guild(guild).level_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the level role to {role.mention}, {author.name}.")
        
        elif option.lower() == "staff":
            # Set the respective role..
            await self.config.guild(guild).staff_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the staff role to {role.mention}, {author.name}.")

        elif option.lower() == "jail":
            # Set the respective role..
            await self.config.guild(guild).jail_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the jailed role to {role.mention}, {author.name}.")
        
        elif option.lower() == "manager":
            
            await self.config.guild(guild).manager_role.set(role.id)
            
            await ctx.send(f"You have successfully set the manager role to {role.mention}, {author.name}.")
        
        elif option.lower() == "claimed":
            # Set the respective role..
            await self.config.guild(guild).claimed_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the claimed role to {role.mention}, {author.name}.")
        
        elif option.lower() == "gagged":
            # Set the respective role..
            await self.config.guild(guild).gagged_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the gagged role to {role.mention}, {author.name}.")
        
        elif option.lower() == "id":
            # Set the respective role..
            await self.config.guild(guild).id_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the ID-verified role to {role.mention}, {author.name}.")
            
        else:
            await ctx.send("You need to enter a valid option and / or role.")
            return

    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def multi_roles(self, ctx, option: str, suboption: str, *, roles: discord.Role):
        """ Set the roles needed for kinkify. Options: [immunity_roles, gag_immunity, jail_immunity]. \n Suboptions: [add, set, remove] for immunity roles. """
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'multi_roles' sub-command of 'kinkify settings' command.")
            return
        
        # Determine all possible roles calls.

        if option.lower() == "immunity":
            roleids = []
            final_message = ""
            preexisting_managers = await self.config.guild(guild).immunity()
            preexisting_roles = preexisting_managers['roles']
            
            if suboption.lower() == "set":
                
                if type(roles) == discord.Role:
                    preexisting_managers['roles'] = roles.id
                    await self.config.guild(guild).immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully set the general immunity roles to the following: {roles.mention}.")
                elif type(roles) == list:
                
                    for mgr in roles[:1]:
                        roleids.append(mgr.id)
                        final_message += f"{mgr.mention}"
                        
                    last_item = mgr[-1]
                    final_message += f"{last_item.mention} \n"
                    roleids.append(last_item.id)
                    preexisting_managers['roles'] = roleids
                    await self.config.guild(guild).immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully set the general immunity roles to the following: \n" + final_message)
                else:
                    await ctx.send("You need to enter a role or multiple roles.")
                    
            elif suboption.lower() == "remove":
                
                if preexisting_roles == []:
                    await ctx.send("There aren't any pre-existing general immunity roles.")
                    return
                
                if type(roles) == discord.Role:
                    preexisting_roles.remove(roles.id)
                    preexisting_managers['roles'] = preexisting_roles
                    await self.config.guild(guild).immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully removed {roles.mention} from the general immunity roles.")
                elif type(roles) == list:
                
                    for mgr in roles:
                        if mgr.id in preexisting_roles:
                            preexisting_roles.remove(mgr.id)
                        roleids.append(mgr.id)
                        final_message += f"{mgr.mention}"
                        
                    preexisting_managers['roles'] = preexisting_roles
                    
                    await self.config.guild(guild).immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully remove the following general immunity roles: \n" + final_message)
                else:
                    await ctx.send("You need to enter a single role or multiple roles.")
                    
            elif suboption.lower() == "add":
                
                if type(roles) == discord.Role:
                    preexisting_roles.append(roles.id)
                    preexisting_managers['roles'] = preexisting_roles
                    await self.config.guild(guild).immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully added {roles.mention} to the general immunity roles.")
                    
                elif type(roles) == list:
                
                    for mgr in roles:
                        if mgr.id not in preexisting_roles:
                            preexisting_roles.append(mgr.id)
                            final_message += f"{mgr.mention}"
                    preexisting_managers['roles'] = preexisting_roles
                    
                    await self.config.guild(guild).immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully added the following general immunity roles: \n" + final_message)
                else:
                    await ctx.send("You need to enter a single role or multiple.")
                    return
            else:
                await ctx.send("You need to enter either of three suboptions: add, remove, set.")
                return
        elif option.lower() == "jail_immunity":
            roleids = []
            final_message = ""
            preexisting_managers = await self.config.guild(guild).jail_immunity()
            preexisting_roles = preexisting_managers['roles']
            
            
            
            
            if suboption.lower() == "set":
                
                if type(roles) == discord.Role:
                    preexisting_managers['roles'] = roles.id
                    await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully set the jail immunity roles to the following: {roles.mention}.")
                elif type(roles) == list:
                
                    for mgr in roles[:1]:
                        roleids.append(mgr.id)
                        final_message += f"{mgr.mention}"
                        
                    last_item = mgr[-1]
                    final_message += f"{last_item.mention} \n"
                    roleids.append(last_item.id)
                    preexisting_managers['roles'] = roleids
                    await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully set the jail immunity roles to the following: \n" + final_message)
                else:
                    await ctx.send("You need to enter a role or multiple roles.")
                    
            elif suboption.lower() == "remove":
                
                if preexisting_roles == []:
                    await ctx.send("There aren't any pre-existing jail immunity roles.")
                    return
                
                if type(roles) == discord.Role:
                    preexisting_roles.remove(roles.id)
                    preexisting_managers['roles'] = preexisting_roles
                    await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully removed {roles.mention} from the jail immunity roles.")
                elif type(roles) == list:
                
                    for mgr in roles:
                        if mgr.id in preexisting_roles:
                            preexisting_roles.remove(mgr.id)
                        roleids.append(mgr.id)
                        final_message += f"{mgr.mention}"
                        
                    preexisting_managers['roles'] = preexisting_roles
                    
                    await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully remove the following jail immunity roles: \n" + final_message)
                else:
                    await ctx.send("You need to enter a single role or multiple roles.")
                    
            elif suboption.lower() == "add":
                
                if type(roles) == discord.Role:
                    preexisting_roles.append(roles.id)
                    preexisting_managers['roles'] = preexisting_roles
                    await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully added {roles.mention} to the jail immunity roles.")
                    
                elif type(roles) == list:
                
                    for mgr in roles:
                        if mgr.id not in preexisting_roles:
                            preexisting_roles.append(mgr.id)
                            final_message += f"{mgr.mention}"
                    preexisting_managers['roles'] = preexisting_roles
                    
                    await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully added the following jail immunity roles: \n" + final_message)
                else:
                    await ctx.send("You need to enter a single role or multiple.")
                    return
            else:
                await ctx.send("You need to enter either of three suboptions: add, remove, set.")
                return
        elif option.lower() == "gag_immunity":
            roleids = []
            final_message = ""
            preexisting_managers = await self.config.guild(guild).gag_immunity()
            preexisting_roles = preexisting_managers['roles']
            
            
            
            
            if suboption.lower() == "set":
                
                if type(roles) == discord.Role:
                    preexisting_managers['roles'] = roles.id
                    await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully set the gag immunity roles to the following: {roles.mention}.")
                elif type(roles) == list:
                
                    for mgr in roles[:1]:
                        roleids.append(mgr.id)
                        final_message += f"{mgr.mention}"
                        
                    last_item = mgr[-1]
                    final_message += f"{last_item.mention} \n"
                    roleids.append(last_item.id)
                    preexisting_managers['roles'] = roleids
                    await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully set the gag immunity roles to the following: \n" + final_message)
                else:
                    await ctx.send("You need to enter a role or multiple roles.")
                    
            elif suboption.lower() == "remove":
                
                if preexisting_roles == []:
                    await ctx.send("There aren't any pre-existing jail immunity roles.")
                    return
                
                if type(roles) == discord.Role:
                    preexisting_roles.remove(roles.id)
                    preexisting_managers['roles'] = preexisting_roles
                    await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully removed {roles.mention} from the gag immunity roles.")
                elif type(roles) == list:
                
                    for mgr in roles:
                        if mgr.id in preexisting_roles:
                            preexisting_roles.remove(mgr.id)
                        roleids.append(mgr.id)
                        final_message += f"{mgr.mention}"
                        
                    preexisting_managers['roles'] = preexisting_roles
                    
                    await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully remove the following gag immunity roles: \n" + final_message)
                else:
                    await ctx.send("You need to enter a single role or multiple roles.")
                    
            elif suboption.lower() == "add":
                
                if type(roles) == discord.Role:
                    preexisting_roles.append(roles.id)
                    preexisting_managers['roles'] = preexisting_roles
                    await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully added {roles.mention} to the gag immunity roles.")
                    
                elif type(roles) == list:
                
                    for mgr in roles:
                        if mgr.id not in preexisting_roles:
                            preexisting_roles.append(mgr.id)
                            final_message += f"{mgr.mention}"
                    preexisting_managers['roles'] = preexisting_roles
                    
                    await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                    await ctx.send(f"You have successfully added the following gag immunity roles: \n" + final_message)
                else:
                    await ctx.send("You need to enter a single role or multiple.")
                    return
            else:
                await ctx.send("You need to enter either of three suboptions: add, remove, set.")
                return
        else:
            await ctx.send("You need to enter a valid option and / or role.")
            return
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def resetlogs(self, ctx, option: str):
        """ Reset the claim list or the user profiles. Options: [all, claims, users]"""
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'resetlogs' sub-command of 'kinkify settings' command.")
            return
        option = option.lower()
        # Determine all possible roles calls. 
        if option == "all":
            await ctx.send("You reset all logs.")
            await self.config.guild(guild).member_claims.set({})
            await self.config.guild(guild).user_profiles.set({})
        elif option == "claims":
            await ctx.send("You reset the claims.")
            await self.config.guild(guild).member_claims.set({})
        elif option == "users":
            await ctx.send("You reset the user profiles.")
            await self.config.guild(guild).user_profiles.set({})
        else:
            await ctx.send("You need to enter a valid option.")
            return
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def serversafeword(self, ctx, *, safeword: str):
        """ Set the server safeword! Default: code red"""
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'serversafeword' sub-command of 'kinkify settings' command.")
            return
        option = option.lower()
        # Determine all possible roles calls. 
        await self.config.guild(guild).safeword.set(safeword)
    
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def immunemembers(self, ctx, option: str, suboption: str, *, members: discord.Member):
        """ Set members that are immune. Options are: [immunity, gag_immunity, jail_immunity]. \n Suboptions are: [add, set, remove] for them. """
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'immunemembers' sub-command of 'kinkify settings' command.")
            return
        
        # Determine all possible roles calls.
        if option.lower() == "immunity":
            roleids = []
            final_message = ""
            preexisting_managers = await self.config.guild(guild).immunity()
            preexisting_roles = preexisting_managers['members']
            
            if suboption.lower() == "set":
                for mgr in members[:1]:
                    roleids.append(mgr.id)
                    final_message += f"{mgr.mention}"
                    
                last_item = mgr[-1]
                final_message += f"{last_item.mention} \n"
                roleids.append(last_item.id)
                preexisting_managers['members'] = roleids
                await self.config.guild(guild).immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully set the general immunity members to the following: \n" + final_message)
                
            elif suboption.lower() == "remove":
                if preexisting_roles == []:
                    await ctx.send("There aren't any pre-existing members with general immunity.")
                    return
                
                for mgr in members:
                    if mgr.id in preexisting_roles:
                        preexisting_roles.remove(mgr.id)
                    roleids.append(mgr.id)
                    final_message += f"{mgr.mention}"
                    
                preexisting_managers['roles'] = preexisting_roles
                
                await self.config.guild(guild).immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully removed the following general immunity members: \n" + final_message)
            elif suboption.lower() == "add":

                for mgr in members:
                    if mgr.id not in preexisting_roles:
                        preexisting_roles.append(mgr.id)
                        final_message += f"{mgr.mention}"
                preexisting_managers['members'] = preexisting_roles
                
                await self.config.guild(guild).immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully added the following general immunity members: \n" + final_message)
            else:
                await ctx.send("You need to enter either of three suboptions: add, remove, set.")
                return
        elif option.lower() == "jail_immunity":
            roleids = []
            final_message = ""
            preexisting_managers = await self.config.guild(guild).jail_immunity()
            preexisting_roles = preexisting_managers['members']
            
                    
            if suboption.lower() == "set":
                for mgr in members[:1]:
                    roleids.append(mgr.id)
                    final_message += f"{mgr.mention}"
                    
                last_item = mgr[-1]
                final_message += f"{last_item.mention} \n"
                roleids.append(last_item.id)
                preexisting_managers['members'] = roleids
                await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully set the jail immunity members to the following: \n" + final_message)
                
            elif suboption.lower() == "remove":
                if preexisting_roles == []:
                    await ctx.send("There aren't any pre-existing jail immunity members.")
                    return
                
                for mgr in members:
                    if mgr.id in preexisting_roles:
                        preexisting_roles.remove(mgr.id)
                    roleids.append(mgr.id)
                    final_message += f"{mgr.mention}"
                    
                preexisting_managers['members'] = preexisting_roles
                
                await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully remove the following jail immunity members: \n" + final_message)
            elif suboption.lower() == "add":

                for mgr in members:
                    if mgr.id not in preexisting_roles:
                        preexisting_roles.append(mgr.id)
                        final_message += f"{mgr.mention}"
                preexisting_managers['members'] = preexisting_roles
                
                await self.config.guild(guild).jail_immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully added the following jail immunity members: \n" + final_message)
            else:
                await ctx.send("You need to enter either of three suboptions: add, remove, set.")
                return   
        elif option.lower() == "gag_immunity":
            roleids = []
            final_message = ""
            preexisting_managers = await self.config.guild(guild).gag_immunity()
            preexisting_roles = preexisting_managers['members']
            
            if suboption.lower() == "set":
                for mgr in members[:1]:
                    roleids.append(mgr.id)
                    final_message += f"{mgr.mention}"
                    
                last_item = mgr[-1]
                final_message += f"{last_item.mention} \n"
                roleids.append(last_item.id)
                preexisting_managers['members'] = roleids
                await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully set the gag immunity members to the following: \n" + final_message)
                
            elif suboption.lower() == "remove":
                if preexisting_roles == []:
                    await ctx.send("There aren't any pre-existing gag immunity roles.")
                    return
                
                for mgr in members:
                    if mgr.id in preexisting_roles:
                        preexisting_roles.remove(mgr.id)
                    roleids.append(mgr.id)
                    final_message += f"{mgr.mention}"
                    
                preexisting_managers['members'] = preexisting_roles
                
                await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully remove the following gag immunity members: \n" + final_message)
            elif suboption.lower() == "add":

                for mgr in members:
                    if mgr.id not in preexisting_roles:
                        preexisting_roles.append(mgr.id)
                        final_message += f"{mgr.mention}"
                preexisting_managers['members'] = preexisting_roles
                
                await self.config.guild(guild).gag_immunity.set(preexisting_managers)
                await ctx.send(f"You have successfully added the following gag immunity members: \n" + final_message)
            else:
                await ctx.send("You need to enter either of three suboptions: add, remove, set.")
                return

        else:
            await ctx.send("You need to enter a valid option and / or member(s).")
            return
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def show_settings(self, ctx):
        
        """ View the settings for the Overseer Aspect. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        all_embeds = []
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'showsettings' sub-command of 'kinkify settings' command.")
            return
        
        # Collect all the booleans
        task_system_bool = await self.config.guild(guild).enable_task_system()
        task_member_suggestion_bool = await self.config.guild(guild).enable_task_member_suggestion()
        
        jail_bool = await self.config.guild(guild).enable_jail()
        jail_log_bool = await self.config.guild(guild).enable_jail_logging()
        staff_jail_immunity_bool = await self.config.guild(guild).enable_staff_jail_immunity()
        ask_jail_bool = await self.config.guild(guild).enable_ask_jail()
        
        gag_bool = await self.config.guild(guild).enable_gag()
        staff_gag_immunity_bool = await self.config.guild(guild).enable_staff_gag_immunity()
        gag_owned_sub_bool = await self.config.guild(guild).enable_gag_owned_sub()
        gag_preference_bool = await self.config.guild(guild).enable_gag_preference()
        
        claims_bool = await self.config.guild(guild).enable_claims()
        claims_strikes_bool = await self.config.guild(guild).enable_claims_strikes()
        claims_multiclaim_bool = await self.config.guild(guild).enable_claims_multiclaim()
        
        headspace_bool = await self.config.guild(guild).enable_headspace()
        headspace_logging_bool = await self.config.guild(guild).enable_headspace_logging()

        
        
        # Collect Misc.
        
        manager = await self.config.guild(guild).manager_role()
        immunes = await self.config.guild(guild).immunity()
        jail_immunes = await self.config.guild(guild).jail_immunity()
        gag_immunes = await self.config.guild(guild).gag_immunity()
        
        immune_members = immunes['members']
        jail_immune_members = jail_immunes['members']
        gag_immune_members = gag_immunes['members']
        
        # Immune Members
        try:
            immune_members_list = []
            for member in immune_members:
                try:
                    memb_temp = get(guild.members, id = member)
                except:
                    memb_temp = "[Not found]"
                immune_members_list.append(memb_temp.mention)
            
            memblist = ""
            if len(immune_members_list) == 1:
                memblist = f"{immune_members_list[0]}"
            else:
                for mentions in immune_members_list[:1]:
                    memblist += f"{mentions}, "
                memblist += f"{immune_members_list[len(immune_members_list)-1]}"
            immune_members_list = memblist
        except:
            immune_members_list = "Not set."
        
        # Immune Jail Members
        try:
            jail_immune_members_list = []
            for member in jail_immune_members:
                try:
                    memb_temp = get(guild.members, id = member)
                except:
                    memb_temp = "[Not found]"
                jail_immune_members_list.append(memb_temp.mention)
            
            memblist = ""
            if len(jail_immune_members_list) == 1:
                memblist = f"{jail_immune_members_list[0]}"
            else:
                for mentions in jail_immune_members_list[:1]:
                    memblist += f"{mentions}, "
                memblist += f"{jail_immune_members_list[len(jail_immune_members_list)-1]}"
            jail_immune_members_list = memblist
        except:
            jail_immune_members_list = "Not set."
        
        try:
            gag_immune_members_list = []
            for member in gag_immune_members:
                try:
                    memb_temp = get(guild.members, id = member)
                except:
                    memb_temp = "[Not found]"
                gag_immune_members_list.append(memb_temp.mention)
            
            memblist = ""
            if len(gag_immune_members_list) == 1:
                memblist = f"{gag_immune_members_list[0]}"
            else:
                for mentions in gag_immune_members_list[:1]:
                    memblist += f"{mentions}, "
                memblist += f"{gag_immune_members_list[len(gag_immune_members_list)-1]}"
            gag_immune_members_list = memblist
        except:
            gag_immune_members_list = "Not set."
        
        
        # Collect all roles.
        immune_roles = immunes['roles']
        jail_immune_roles = jail_immunes['roles']
        gag_immune_roles = gag_immunes['roles']


        
        try:
            immune_role = immune_roles
            immune_role = [role.mention for role in immune_role]
            rolelist = ""
            if len(immune_role) == 1:
                rolelist = f"{immune_role[0]}"
            else:
                for mentions in immune_role[:1]:
                    rolelist += f"{mentions}, "
                rolelist += f"{immune_role[len(immune_role)-1]}"
            immune_role = rolelist
        except:
            immune_role = "Not set."
        
        try:
            jail_immune_role = jail_immune_roles
            jail_immune_role = [role.mention for role in jail_immune_role]
            rolelist = ""
            if len(jail_immune_role) == 1:
                rolelist = f"{jail_immune_role[0]}"
            else:
                for mentions in jail_immune_role[:1]:
                    rolelist += f"{mentions}, "
                rolelist += f"{jail_immune_role[len(jail_immune_role)-1]}"
            jail_immune_role = rolelist
        except:
            jail_immune_role = "Not set."
            
        try:
            gag_immune_role = gag_immune_roles
            gag_immune_role = [role.mention for role in gag_immune_role]
            rolelist = ""
            if len(gag_immune_role) == 1:
                rolelist = f"{gag_immune_role[0]}"
            else:
                for mentions in gag_immune_role[:1]:
                    rolelist += f"{mentions}, "
                rolelist += f"{gag_immune_role[len(gag_immune_role)-1]}"
            gag_immune_role = rolelist
        except:
            gag_immune_role = "Not set."

        try:
            headspace_colour = await self.config.guild(guild).headspace_roles_colour()
            headspace_red, headspace_yellow, headspace_green = get(guild.roles, id=headspace_colour['red']), get(guild.roles, id=headspace_colour['yellow']), get(guild.roles, id=headspace_colour['green'])
            headspace_red, headspace_yellow, headspace_green = headspace_red.mention, headspace_yellow.mention, headspace_green.mention
        except:
            headspace_red, headspace_yellow, headspace_green = "Not set.", "Not set.", "Not set."
        
        try:
            headspace_bdsm =await self.config.guild(guild).headspace_roles_bdsm()
            headspace_dom, headspace_switch, headspace_sub, headspace_none = get(guild.roles, id=headspace_bdsm['dominant']), get(guild.roles, id=headspace_bdsm['switch']), get(guild.roles, id=headspace_bdsm['submissive']), get(guild.roles, id=headspace_bdsm['none'])
            headspace_dom, headspace_switch, headspace_sub, headspace_none = headspace_dom.mention, headspace_switch.mention, headspace_sub.mention, headspace_none.mention
        except:
            headspace_dom, headspace_switch, headspace_sub, headspace_none = "Not set.", "Not set.", "Not set.", "Not set."
        
        try:
            staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
            staff_role = staff_role.mention
        except:
            staff_role = "Not set."
        
        try:
            level_role = get(guild.roles, id= await self.config.guild(guild).level_role())
            level_role = level_role.mention
        except:
            level_role = "Not set."
        
        try:
            nsfw_role = get(guild.roles, id=await self.config.guild(guild).nsfw_role())
            nsfw_role = nsfw_role.mention
        except:
            nsfw_role = "Not set."
            
        try:
            id_role = get(guild.roles, id=await self.config.guild(guild).id_role())
            id_role = id_role.mention
        except:
            id_role = "Not set."

        try:
            sfw_role = get(guild.roles, id=await self.config.guild(guild).sfw_role())
            sfw_role = sfw_role.mention
        except:
            sfw_role = "Not set."
        
        try:
            manager = get(guild.roles, id=await self.config.guild(guild).manager_role())
            manager = manager.mention
        except:
            manager = "Not set."
        
        
        try:
            little_role = get(guild.roles, id=await self.config.guild(guild).little_role())
            little_role = little_role.mention
        except:
            little_role = "Not set."
        
        try:
            jail_role = get(guild.roles, id=await self.config.guild(guild).jail_role())
            jail_role = jail_role.mention
        except:
            jail_role = "Not set."

        try:
            claimed_role = get(guild.roles, id=await self.config.guild(guild).claimed_role())
            claimed_role = claimed_role.mention
        except:
            claimed_role = "Not set."

        try:
            gagged_role = get(guild.roles, id=await self.config.guild(guild).gagged_role())
            gagged_role = gagged_role.mention
        except:
            gagged_role = "Not set."

        # Collect all the channels
            
        try:
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())
            log_channel = log_channel.mention
        except:
            log_channel = "Not set."

        try:
            modlog_channel = get(guild.channels, id=await self.config.guild(guild).modlog_channel())
            modlog_channel = modlog_channel.mention
        except:
            modlog_channel = "Not set."

        try:
            jail_log_channel = get(guild.channels, id=await self.config.guild(guild).jail_log_channel())
            jail_log_channel = jail_log_channel.mention
        except:
            jail_log_channel = "Not set."

        try:
            jail_channel = get(guild.channels, id=await self.config.guild(guild).jail_channel())
            jail_channel = jail_channel.mention
        except:
            jail_channel = "Not set."
        
        try:
            staff_channel = get(guild.channels, id=await self.config.guild(guild).staff_channel())
            staff_channel = staff_channel.mention
        except:
            staff_channel = "Not set."

        try:
            boundaries_channel = get(guild.channels, id=await self.config.guild(guild).boundaries())
            boundaries_channel = boundaries_channel.mention
        except:
            boundaries_channel = "Not set."

        try:
            claim_channel = get(guild.channels, id=await self.config.guild(guild).claim_channel())
            claim_channel = claim_channel.mention
        except:
            claim_channel = "Not set."

        try:
            task_channel = get(guild.channels, id=await self.config.guild(guild).task_channel())
            task_channel = task_channel.mention
        except:
            task_channel = "Not set."

        
        # Main Page
        main = "You can use the emojis below to navigate the settings. \nPage 2 of 5 will detail all the enabled or disabled settings.\nPage 3 of 5 will show you the roles of Kinkify. \nPage 4 of 5 will show the channels of Kinkify. \nPage 5 of 5 will show immune members."
        main_embed = discord.Embed(title="**Kinkify Settings**", description="**Main Page**: \n" + main, color=clr)
        main_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        main_embed.add_field(name="Date", value="{}".format(timestamp))
        main_embed.set_footer(text="Page    1 / 5")
        all_embeds.append(main_embed)
        
        # Boolean: All enabled / disabled settings
        bools = f"**Jail**: \n **Enable Jail:** {jail_bool} \n**Enable Jail Logging:** {jail_log_bool} \n**Enable Ask Before Jailing:** {ask_jail_bool} \n**Enable Staff Jail Immunity:** {staff_jail_immunity_bool} \n\n **Gag Command**: \n **Enable Gag Feature:** {gag_bool} \n**Enable Staff Gag Immunity:** {staff_gag_immunity_bool} \n**Enable Gagging Owned Subs:** {gag_owned_sub_bool} \n**Enable Gag Preferences:** {gag_preference_bool} \n\n **Claiming**: \n **Enable Claims:** {claims_bool} \n**Enable Striking (in Claims):** {claims_strikes_bool} \n**Enable Multiple Claims:** {claims_multiclaim_bool} \n\n **Headspace**: \n **Enable Headspace Commands:** {headspace_bool} \n**Enable Headspace Logging:** {headspace_logging_bool} \n\n **Tasks:** \n**Enable Task System:** {task_system_bool} \n**Enable Member Task Suggestion:** {task_member_suggestion_bool}"
        bool_embed = discord.Embed(title="**Kinkify Settings**", description="# **Enabled / Disabled Settings**:\n" + bools, color=clr)
        bool_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        bool_embed.add_field(name="Date", value="{}".format(timestamp))
        bool_embed.set_footer(text="Page    2 / 5")
        all_embeds.append(bool_embed)
        
        # Moderation: All settings
        mods = f"# **Roles:**\n**ID-verified Role**: {id_role} \n**NSFW Role**: {nsfw_role} \n**SFW Role**: {sfw_role} \n**Leveled Role**: {level_role} \n**Little Role**: {little_role} \n**Staff Role:** {staff_role} \n**Manager Role**: {manager} \n**Jail Role**: {jail_role} \n**Claimed Role**: {claimed_role} \n**Gagged Role**: {gagged_role} \n**Immune Roles**: {immune_role} \n**Jail-Immune Roles**: {jail_immune_role} \n**Gag-Immune Roles**: {gag_immune_role} \n\n**Headspace Roles**: \n\n**Headspace Green**: {headspace_green} \n**Headspace Yellow**: {headspace_yellow} \n**Headspace Red**: {headspace_red} \n**Headspace Dominant**: {headspace_dom} \n**Headspace Switch**: {headspace_switch} \n**Headspace Submissive**: {headspace_sub} \n**Headspace None**: {headspace_none}"
        mod_embed = discord.Embed(title="**Kinkify Settings**", description="# **Role Settings**:\n" + mods, color=clr)
        mod_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        mod_embed.add_field(name="Date", value="{}".format(timestamp))
        mod_embed.set_footer(text="Page    3 / 5")
        all_embeds.append(mod_embed)
        
        
        # Verification: All settings
        
        verif = f"# **Channels**:\n**Log Channel**: {log_channel} \n**Mod Log Channel**: {modlog_channel} \n **Jail Log Channel**: {jail_log_channel} \n**Staff Channel**: {staff_channel} \n**Jail Channel**: {jail_channel} \n**Boundaries Channel**: {boundaries_channel} \n**Claim Channel**: {claim_channel} \n**Task Channel**: {task_channel}"
        ver_embed = discord.Embed(title="**Kinkify Settings**", description="# **Channel Settings**:\n" + verif, color=clr)
        ver_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        ver_embed.add_field(name="Date", value="{}".format(timestamp))
        ver_embed.set_footer(text="Page    4 / 5")
        all_embeds.append(ver_embed)
        
        verif_2 = f"# **Miscellaneous:** \n**Immune Members:** {immune_members_list} \n\n**Jail-Immune Members**: {jail_immune_members_list} \n\n**Gag-Immune Members**: {gag_immune_members_list}"
        ver2_embed = discord.Embed(title="**Kinkify Settings**", description="# **Immune Members**:\n" + verif_2, color=clr)
        ver2_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        ver2_embed.add_field(name="Date", value="{}".format(timestamp))
        ver2_embed.set_footer(text="Page    5 / 5")
        all_embeds.append(ver2_embed)
        
        current_page = 0
        total_pages_items = 5
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


