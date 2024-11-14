import discord, json, random, asyncio, logging, traceback, redbot.core.data_manager, datetime, re
from redbot.core import commands, app_commands, utils
from redbot.core.bot import Red
from redbot.core.config import Config
from datetime import timedelta
from discord.utils import get

from ..abc import MixinMeta, CompositeMetaClass
from .settings import Settings

async def staff_check(self, ctx, member: discord.Member) -> bool:
        """" Check if a user has a mod or staff role. """
        
        guild = ctx.guild

        
        if member not in guild.members:
            return False
        
        if redbot.core.utils.mod.is_mod_or_superior(self, member):
            return True
        else:
            return False

def element_check(self, ctx, search_through, property: str, search_property):
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

    


class Moderation(MixinMeta):
    
    """
    Moderation Commands / Methods.
    """
    
    # MODERATION COMMANDS
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str=None):
        """ Kick a user (with an optional reason). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        is_staff = False
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild)
        adminroles = await Red.get_admin_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if len(modroles) == 0 or len(adminroles) == 0 or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif len([role for role in adminroles if role in author.roles ]) == 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif len([role for role in adminroles if role in author.roles ]) > 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    is_staff = True
            elif staffrole in member.roles:
                is_staff = True
        else:
            await ctx.send("My apologies, however, this member is not in the server.")
            is_staff = False
            return
        
        # Check the rest
        if reason == None:
            reason = "None given."
        
        if member == author:
            await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to kick yourself. Doing so amounts to a foolish action I will not tolerate. Behave yourself.")
            return
        elif member.id in [852263086714257440, 1191841714504212490]:
            await ctx.send(f"My apologies. I can not allow you to kick my creator or myself.")
            return

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'kick' command.")
            return


        # Get user, make sure there is existing log
        kick_logs = await self.config.guild(guild).kick_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
    
        user_logs = await self.config.guild(guild).users()
        target = None
        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
            
        if target == None:
            user_logs[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : [guild.name, guild.id],
                "kicks" : [], # Kick logs
                "bans" : [], # Ban logs
                "quarantines" : [], # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]

        # Make sure staff is only kicked on purpose
        if is_staff == True:
            await ctx.send("Dear, are you sure that you want to kick this member? They are fellow staff. Reply with 'yes' ('y') or 'no' ('n').")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                await ctx.send(f"I will now continue with your requested order, {author.name}.")
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return    
            
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Kick **", description=f"**Attention.** A user has been kicked.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Kick **", description=f"**Attention.** A user has been kicked. \n They have been deemed unworthy of staying in the server.", color=clr)
            public_log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            number = len(target["kicks"]) + 1
            
            for_kick_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "kick",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed intolerable within {guild.name} for your behaviour, thus you were kicked. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            kick_logs["logs"].append(for_kick_log)
            incidents_logs["logs"].append(for_incident_log)
            target["kicks"].append(for_kick_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await guild.kick(member, reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have kicked member {member.name}. I gave them notice of their demise.")
                else:
                    await ctx.send(f"Dear {author.name}, you have kicked member {member.name}. I could not contact this member and inform them. Either the action is disabled, or they can not be contacted.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to kick this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).kick_logs.set(kick_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            # (Mod)Log embed
            log_embed = discord.Embed(title="**Moderation Action: Kick **", description=f"**Attention.** A user has been kicked.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            

            # Post the log messages.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            
            # Create the bot-internal logs.
            number = len(target["kicks"]) + 1
            
            for_kick_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "kick",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }
            
            # DM the user.
            Goodbye = f"Attention, {member.mention}, \n you have been deemed intolerable within {guild.name} for your behaviour, thus you were kicked. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful=False
            
            # Set the logs
            kick_logs["logs"].append(for_kick_log)
            incidents_logs["logs"].append(for_incident_log)
            target["kicks"].append(for_kick_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await guild.kick(member, reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have kicked member {member.name}. I gave them notice of their demise.")
                else:
                    await ctx.send(f"Dear {author.name}, you have kicked member {member.name}. I could not contact this member and inform them. Either the action is disabled, or they could not be contacted.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to kick this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).kick_logs.set(kick_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)
            

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def quarantine(self, ctx, member: discord.Member, *, reason: str=None):
        """ Quarantine a user (with an optional reason). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        is_staff = False
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild) 
        adminroles = await Red.get_mod_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        quarantinerole = get(guild.roles, id = await self.config.guild(guild).quarantine_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        quarantine_channel = get(guild.channels, id = await self.config.guild(guild).quarantine_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or modlog_channel == None or quarantine_channel == None or quarantinerole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif len([role for role in adminroles if role in author.roles ]) == 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif len([role for role in adminroles if role in author.roles ]) > 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    is_staff = True
            elif staffrole in member.roles:
                is_staff = True
        else:
            await ctx.send("My apologies, however, this member is not in the server.")
            is_staff = False
            return

        
        if reason == None:
            reason = "None given."
        
        if member == author:
            await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to quarantine yourself. Doing so amounts to a foolish action I will not tolerate. Behave yourself.")
            return
        elif member.id == 852263086714257440:
            await ctx.send(f"My apologies, dear {author.name}, I can not allow you to kick my creator.")
            return
        elif member.id == 1191841714504212490:
            await ctx.send(f"My apologies, dear {author.name}, I can not quarantine myself.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'quarantine' command.")
            return


        # Get user, make sure there is existing log
        quarantine_logs = await self.config.guild(guild).quarantine_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
        user_logs = await self.config.guild(guild).users()
        target = None
        logged_already = None
        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
        
        loggedcheck = element_check(self, ctx, quarantine_logs, "member_id", member.id)
        if loggedcheck[0] == True:
            logged_already = loggedcheck[1]

        
        
        if logged_already != None and quarantinerole in member.roles:
            await ctx.send("This user is already quarantined. Do you want to unquarantine them?")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                back_roles = []
                for rls in logged_already["roles"]:
                    if get(guild.roles, id = rls) != None:
                        back_roles.append(get(guild.roles, id = rls))
                await member.edit(roles=back_roles)
                await ctx.send(f"You have successfully unquarantined {member.name}, {author.name}.")
                quarantine_logs.pop(str(member.id))
                try:
                    await self.config.guild(guild).quarantines.set(quarantine_logs)
                except:
                    return
                return
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return  
        

        if target == None:
            temp_list_roles = []
            for rls in member.roles:
                temp_list_roles.append(rls.id)
            user_logs[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : [guild.name, guild.id],
                "kicks" : [], # Kick logs
                "bans" : [], # Ban logs
                "quarantines" : [], # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0, # incident count
                "roles" : temp_list_roles,
            }
            target = user_logs[member.id]

        # Make sure staff is only kicked on purpose
        if is_staff == True:
            await ctx.send("Dear, are you sure that you want to quarantine this member? They are fellow staff. Reply with 'yes' ('y') or 'no' ('n').")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                await ctx.send(f"I will now continue with your requested order, {author.name}.")
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return    

        
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Quarantine **", description=f"**Attention.** A user has been quarantined in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Quarantine **", description=f"**Attention.** A user has been quarantined in {guild.name}. \n Their permissions have been locked, and their fate is up for investigation..", color=clr)
            public_log_embed.add_field(name="**Reason:**", value=reason)
            
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            temp_list_roles = []
            for rls in member.roles:
                temp_list_roles.append(rls.id)
            
            number = len(target["quarantines"]) + 1
            
            for_quarantine_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "quarantine",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed suspicious or otherwise worthy of investigation within {guild.name} for your behaviour, thus you were quarantined. The reason: {reason} \n My deepest apologies."
            
            if dm_bool==True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            quarantine_logs[member.id] = for_quarantine_log
            incidents_logs["logs"].append(for_incident_log)
            target["quarantines"].append(for_quarantine_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await member.edit(roles=[quarantinerole])
                if successful:
                    await ctx.send(f"Dear {author.name}, you have quarantined member {member.name}. I gave them notice of this.")
                else:
                    await ctx.send(f"Dear {author.name}, you have quarantined member {member.name}. I could not contact this member and inform them. Either, the DM feature is disabled, or they can not be contacted by me.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to quarantine this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).quarantine_logs.set(quarantine_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Quarantine **", description=f"**Attention.** A user has been quarantined in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            
            # Post the log message.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            temp_list_roles = []
            for rls in member.roles:
                temp_list_roles.append(rls.id)
            
            number = len(target["quarantines"]) + 1
            
            for_quarantine_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "quarantine",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed suspicious or otherwise worthy of investigation within {guild.name} for your behaviour, thus you were quarantined. The reason: {reason} \n My deepest apologies."
            
            if dm_bool==True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            quarantine_logs[member.id]=for_quarantine_log
            incidents_logs["logs"].append(for_incident_log)
            target["quarantines"].append(for_quarantine_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await member.edit(roles=[quarantinerole])
                if successful:
                    await ctx.send(f"Dear {author.name}, you have quarantined member {member.name}. I gave them notice of this.")
                else:
                    await ctx.send(f"Dear {author.name}, you have quarantined member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or they could not be contacted by me.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to quarantine this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).quarantine_logs.set(quarantine_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
    
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, time: int, *, reason: str=None):
        """ Timeout a user (with duration in seconds, and an optional reason). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        is_staff = False
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild) 
        adminroles = await Red.get_mod_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return

        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif len([role for role in adminroles if role in author.roles ]) == 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif len([role for role in adminroles if role in author.roles ]) > 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    is_staff = True
            elif staffrole in member.roles:
                is_staff = True
        else:
            await ctx.send("My apologies, however, this member is not in the server.")
            is_staff = False
            return
        
        if reason == None:
            reason = "None given."
        
        if member == author:
            await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to timeout yourself. Doing so amounts to a foolish action I will not tolerate. Behave yourself.")
            return
        elif member.id == 852263086714257440:
            await ctx.send(f"My apologies, dear {author.name}, I can not allow you to kick my creator.")
            return
        elif member.id == 1191841714504212490:
            await ctx.send(f"My apologies, dear {author.name}, I can not time myself out.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'timeout' command.")
            return


        # Get user, make sure there is existing log
        timeout_logs = await self.config.guild(guild).timeout_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
        user_logs = await self.config.guild(guild).users()
        target = None
        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
            
        if target == None:
            user_logs[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : [guild.name, guild.id],
                "kicks" : [], # Kick logs
                "bans" : [], # Ban logs
                "quarantines" : [], # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]

        # Make sure staff is only kicked on purpose
        if is_staff == True:
            await ctx.send("Dear, are you sure that you want to timeout this member? They are fellow staff. Reply with 'yes' ('y') or 'no' ('n').")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                await ctx.send(f"I will now continue with your requested order, {author.name}.")
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return    
            
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Timeout **", description=f"**Attention.** A user has been put into timeout in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Timeout **", description=f"**Attention.** A user has been put into timeout. \n They need to calm down.", color=clr)
            public_log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            number = len(target["timeouts"]) + 1
            
            for_timeout_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "duration" : time,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "kick",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "duration" : time,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been put into timeout in {guild.name} for your behaviour. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            timeout_logs["logs"].append(for_timeout_log)
            incidents_logs["logs"].append(for_incident_log)
            target["timeouts"].append(for_timeout_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await member.timeout(timedelta(minutes=time), reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have put member {member.name} into timeout. I gave them notice.")
                else:
                    await ctx.send(f"Dear {author.name}, you have put member {member.name} into timeout. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to timeout this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).timeout_logs.set(timeout_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            # (Mod)Log embed
            log_embed = discord.Embed(title="**Moderation Action: Timeout **", description=f"**Attention.** A user has been put into timeout in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            

            # Post the log messages.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            number = len(target["timeouts"]) + 1
            
            # Create the bot-internal logs.
            for_timeout_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "duration" : time,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "kick",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "duration" : time,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }
            
            # DM the user.
            Goodbye = f"Attention, {member.mention}, \n you have been put into timeout in {guild.name} for your behaviour. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            # Set the logs
            timeout_logs["logs"].append(for_timeout_log)
            incidents_logs["logs"].append(for_incident_log)
            target["timeouts"].append(for_timeout_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await member.timeout(timedelta(minutes=time), reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have put member {member.name} into timeout. I gave them notice.")
                else:
                    await ctx.send(f"Dear {author.name}, you have put member {member.name} into timeout. I could not contact this member and inform them. Either the DM feature is disabled, or they could not be contact by me.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to timeout this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).timeout_logs.set(timeout_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)
    
     
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, *, reason: str=None):
        """ Ban a user (with an optional reason). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        is_staff = False
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild) 
        adminroles = await Red.get_mod_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        
        if member in guild.members:
            member = guild.get_member(member.id)
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif len([role for role in adminroles if role in author.roles ]) == 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif len([role for role in adminroles if role in author.roles ]) > 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    is_staff = True
            elif staffrole in member.roles:
                is_staff = True
            
        else:
            is_staff = False
            
            

        
        
        if reason == None:
            reason = "None given."
        
        if member == author:
            await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to ban yourself. Doing so amounts to a foolish action I will not tolerate. Behave yourself.")
            return
        elif member.id == 852263086714257440:
            await ctx.send(f"My apologies, dear {author.name}, I can not allow you to ban my creator.")
            return
        elif member.id == 1191841714504212490:
            await ctx.send(f"My apologies, dear {author.name}, I can not ban myself.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'ban' command.")
            return


        # Get user, make sure there is existing log
        ban_logs = await self.config.guild(guild).ban_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
        user_logs = await self.config.guild(guild).users()
        
        target = None
        for key in user_logs:
            if user_logs[key]["member_id"] == member.id:
                target = user_logs[key]
            
        if target == None:
            user_logs[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : [guild.name, guild.id],
                "kicks" : [], # Kick logs
                "bans" : [], # Ban logs
                "quarantines" : [], # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]

        # Make sure staff is only kicked on purpose
        if is_staff == True:
            await ctx.send("Dear, are you sure that you want to ban this member? They are fellow staff. Reply with 'yes' ('y') or 'no' ('n').")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                await ctx.send(f"I will now continue with your requested order, {author.name}.")
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return    
            
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            # Log Embed
            log_embed = discord.Embed(title="**Moderation Action: Ban **", description=f"**Attention.** A user has been banned from {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Ban **", description=f"**Attention.** A user has been banned from {guild.name}. \n They have been deemed unworthy of staying in the server.", color=clr)
            public_log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            number = len(target["bans"]) + 1
            
            for_ban_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "ban",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed intolerable within {guild.name} for your behaviour, thus you were banned. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            ban_logs[member.id] = for_ban_log
            incidents_logs["logs"].append(for_incident_log)
            target["bans"].append(for_ban_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await guild.ban(member, reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have banned member {member.name}. I gave them notice of their demise.")
                else:
                    await ctx.send(f"Dear {author.name}, you have banned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to ban this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).ban_logs.set(ban_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            # (Mod)Log embed
            log_embed = discord.Embed(title="**Moderation Action: Ban **", description=f"**Attention.** A user has been banned from {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            

            # Post the log messages.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            number = len(target["bans"]) + 1
            
            # Create the bot-internal logs.
            for_ban_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "ban",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }
            
            # DM the user.
            Goodbye = f"Attention, {member.mention}, \n you have been deemed intolerable within {guild.name} for your behaviour, thus you were banned. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            # Set the logs
            ban_logs[member.id]=for_ban_log
            incidents_logs["logs"].append(for_incident_log)
            target["bans"].append(for_ban_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await guild.ban(member, reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have banned member {member.name}. I gave them notice of their demise.")
                else:
                    await ctx.send(f"Dear {author.name}, you have banned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to ban this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).ban_logs.set(ban_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)
            
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason: str=None):
        """ Unban a user (with an optional reason). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target_log = None
        is_staff = False
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild) 
        adminroles = await Red.get_mod_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return

        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return

        
        if reason == None:
            reason = "None given."
        
        if member == author:
            await ctx.send(f"My apologies, dear {author.name}, however, you are a member of this server, and thus not banned.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'unban' command.")
            return


        # Get user, make sure there is existing log
        ban_logs = await self.config.guild(guild).ban_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
        user_logs = await self.config.guild(guild).users()
        
        user_logs = await self.config.guild(guild).users()
        is_in = element_check(self, ctx, user_logs, "member_id", member.id)
        if is_in[0] == False:
            user_logs[member.id] = {
                        "member_id" : member.id,
                        "member_name" : member.name,
                        "guild" : [guild.name, guild.id],
                        "kicks" : [], # Kick logs
                        "bans" : {}, # Ban logs
                        "quarantines" : {}, # Quarantine logs
                        "timeouts" : [], # Timeout logs
                        "warns" : [], # Warn logs
                        "notes" : [], # User notes
                        "threshold" : 0 # incident count
                    }
            target = user_logs[member.id] 
        else:
            target = is_in[1]

            
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            for key in ban_logs:
                if ban_logs[key]['member_id'] == member.id:
                    target_log = ban_logs[key]
            if target_log == None or member in guild.members:
                await ctx.send(f"My apologies, dear {author.name}, but this member is not banned.")
                return
            elif target_log != None:
                try:
                    await guild.unban(member)
                except:
                    await ctx.send(f"My apologies, dear {author.name}, but {member.name} could not be unbanned.")
                    return

                    
                
            # Log Embed
            log_embed = discord.Embed(title="**Moderation Action: Unban **", description=f"**Attention.** A user has been unbanned in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Unban **", description=f"**Attention.** A user has been unbanned in {guild.name}. \n They have been deemed worthy.", color=clr)
            public_log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            
            for_incident_log = {
                "incident_type" : "unban",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id]
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed tolerable within {guild.name}, thus you were unbanned. The reason: {reason}"
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            incidents_logs["logs"].append(for_incident_log)
            target["threshold"] -= 1
            
            # Manage the threshold, and set the user log back
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            if successful:
                    await ctx.send(f"Dear {author.name}, you have unbanned member {member.name}. I gave them notice of their fate")
            else:
                    await ctx.send(f"Dear {author.name}, you have unbanned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            
            ban_logs.pop(str(member.id))
            
            # Save the logs
            await self.config.guild(guild).ban_logs.set(ban_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            for key in ban_logs:
                if ban_logs[key]['member_id'] == member.id:
                    target_log = ban_logs[key]
            if target_log == None or member in guild.members:
                await ctx.send(f"My apologies, dear {author.name}, but this member is not banned.")
                return
            elif target_log != None:
                try:
                    await guild.unban(member)
                except:
                    await ctx.send(f"My apologies, dear {author.name}, but {member.name} could not be unbanned.")
                    return
            
            # (Mod)Log embed
            log_embed = discord.Embed(title="**Moderation Action: Unban **", description=f"**Attention.** A user has been unbanned in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            

            # Post the log messages.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            # Create the bot-internal logs.
            for_ban_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id]
            }
            
            for_incident_log = {
                "incident_type" : "unban",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id]
            }
            
            # DM the user.
            Goodbye = f"Attention, {member.mention}, \n you have been deemed tolerable within {guild.name}, thus you were unbanned. The reason: {reason}"
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            # Set the logs
            incidents_logs["logs"].append(for_incident_log)
            target["threshold"] -= 1
            
            # Manage the threshold, and set the user log back
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            try: 
                await guild.unban(member, reason=reason)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have unbanned member {member.name}. I gave them notice of their fate.")
                else:
                    await ctx.send(f"Dear {author.name}, you have unbanned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            except:
                await ctx.send(f"My apologies, {author.name}, however, I was not able to unban this user. There has been an error. Please attempt again, and contact my Creator.")
                return
            
            ban_logs.pop(member.id)
            # Save the logs
            await self.config.guild(guild).ban_logs.set(ban_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)
    
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx, member: discord.User, *, reason: str=None):
        """ Warn a user (with an optional reason). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        is_staff = False
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild) 
        adminroles = await Red.get_mod_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif len([role for role in adminroles if role in author.roles ]) == 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif len([role for role in adminroles if role in author.roles ]) > 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    is_staff = True
            elif staffrole in member.roles:
                is_staff = True
        else:
            is_staff = False
            if staffrole not in author.roles:
                    await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                    return
                
        if reason == None:
            reason = "None given."
        
        if member == author:
           await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to warn yourself. Doing so amounts to a foolish action I will not tolerate. Behave yourself.")
           return
        elif member.id == 852263086714257440:
            await ctx.send(f"My apologies, dear {author.name}, I can not allow you to warn my creator.")
            return
        elif member.id == 1191841714504212490:
            await ctx.send(f"My apologies, dear {author.name}, I can not warn myself.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'warn' command.")
            return


        # Get user, make sure there is existing log
        warn_logs = await self.config.guild(guild).warn_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
        user_logs = await self.config.guild(guild).users()
        target = None
        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
            
        if target == None:
            user_logs[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : guild.id,
                "kicks" : [], # Kick logs
                "bans" : [], # Ban logs
                "quarantines" : [], # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]
            
        # Make sure staff is only kicked on purpose
        if is_staff == True:
            await ctx.send("Dear, are you sure that you want to warn this member? They are fellow staff. Reply with 'yes' ('y') or 'no' ('n').")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                await ctx.send(f"I will now continue with your requested order, {author.name}.")
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return    
        
        # Number of warns
        warn_number = len(target["warns"]) + 1
        
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Warn **", description=f"**#{warn_number}**\n**Attention.** A user has been warned.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Warn **", description=f"**#{warn_number}**\n **Attention.** A user has been warned.", color=clr)
            public_log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            
            for_warn_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : f"{log_message.jump_url}",
                "server" : [guild.name,guild.id],
                "number_warn" : warn_number
            }
            
            for_incident_log = {
                "incident_type" : "warn",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : f"{log_message.jump_url}",
                "guild" : [guild.name,guild.id],
                "number_warn" : warn_number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been warned within {guild.name} for your behaviour. This is warning #{warn_number}. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
                
                
            warn_logs["logs"].append(for_warn_log)
            incidents_logs["logs"].append(for_incident_log)
            target["warns"].append(for_warn_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            

            # Kick the user and send a message.
            if successful:
                await ctx.send(f"Dear {author.name}, you have warned member {member.name}. I gave them notice of their fate.")
            else:
                await ctx.send(f"Dear {author.name}, you have warned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            
            # Save the logs
            
            await self.config.guild(guild).warn_logs.set(warn_logs) 
            await self.config.guild(guild).users.set(user_logs) 
            await self.config.guild(guild).incident_logs.set(incidents_logs) 
                 
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Warn **", description=f"** #{warn_number}**\n **Attention.** A user has been warned.", color=clr)
            log_embed.add_field(name="**Reason:**", value=reason)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            
            # Post the log messages.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            
            for_warn_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number_warn" : warn_number
            }
            
            for_incident_log = {
                "incident_type" : "warn",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "reason" : reason,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number_warn" : warn_number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been warned within {guild.name} for your behaviour. This is warning #{warn_number}. The reason: {reason} \n My deepest apologies."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            warn_logs.append(for_warn_log)
            incidents_logs.append(for_incident_log)
            target["warns"].append(for_warn_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            if successful:
                await ctx.send(f"Dear {author.name}, you have warned member {member.name}. I gave them notice of their fate.")
            else:
                await ctx.send(f"Dear {author.name}, you have warned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            
            # Save the logs
            
            await self.config.guild(guild).warn_logs.set(warn_logs) 
            await self.config.guild(guild).users.set(user_logs) 
            await self.config.guild(guild).incident_logs.set(incidents_logs) 
 
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unwarn(self, ctx, member: discord.User, number: int):
        """ Unwarn a user."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        is_staff = False
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modroles = await Red.get_mod_roles(ctx.bot, guild) 
        adminroles = await Red.get_mod_roles(ctx.bot, guild)
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif len([role for role in adminroles if role in author.roles ]) == 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif len([role for role in adminroles if role in author.roles ]) > 0 and len([role for role in modroles if role in author.roles]) > 0:
                if len([role for role in adminroles if role in member.roles]) > 0 or len([role for role in modroles if role in member.roles]) > 0:
                    is_staff = True
            elif staffrole in member.roles:
                is_staff = True
        else:
            is_staff=False
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return

        if member == author:
           await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to unwarn yourself. Behave yourself.")
           return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'unwarn' command.")
            return

        if number <=0:
            await ctx.send(f"My apologies, {author.name}, you can only delete warns that exist. Please enter a positive number.")
            return
        
        # Get user, make sure there is existing log
        warn_logs = await self.config.guild(guild).warn_logs()
        incidents_logs = await self.config.guild(guild).incident_logs()
        user_logs = await self.config.guild(guild).users()
        target = None
        target_log = None
        target_warn_log = None
        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
            
        if target == None:
            user_logs[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : [guild.name, guild.id],
                "kicks" : [], # Kick logs
                "bans" : [], # Ban logs
                "quarantines" : [], # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]

        # Make sure staff is only kicked on purpose
        if is_staff == True:
            await ctx.send("Dear, are you sure that you want to unwarn this member? They are fellow staff. Reply with 'yes' ('y') or 'no' ('n').")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond. Your requested order was cancelled.")
                return
            if 'no' in msg.content or 'n' in msg.content:
                await ctx.send(f"As you have seemingly denied the order, it is now cancelled, {author.name}.")
                return
            elif 'yes' in msg.content or 'y' in msg.content:
                await ctx.send(f"I will now continue with your requested order, {author.name}.")
            else:
                await ctx.send(f"My apologies, {author.name}, however, I can only pick up responses that incorporate either a definite 'yes' or 'no'. Please refer to my original message. Your requested order has been cancelled.")
                return    
        
        for lgs in warn_logs:
            if (lgs["member_id"] == member.id and lgs["number_warn"] == number):
                target_log = lgs
                
                        
        if target_log == None:
            await ctx.send(f"My apologies, dear {author.name}, but this member has no warns.")
            return
        elif target_log != None:
            for item in target["warns"]:
                if item["number_warn"] == number:
                    target_warn_log = item
            if target_warn_log != None:
                target["warns"].remove(target_warn_log)
                warn_logs.remove(target_log)
            else:
                await ctx.send(f"My apologies, {author.name}, but I could not fulfill your command.")
                return
        
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Unwarn **", description=f"**#{number}**\n **Attention.** A user has been unwarned.", color=clr)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Public Log Embed
            public_log_embed = discord.Embed(title="**Moderation Action: Unwarn **", description=f"**#{number}**\n **Attention.** A user has been unwarned.", color=clr)
            
            if member not in guild.members:
                public_log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                public_log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            public_log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            public_log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            public_log_embed.set_footer(text="Date - {}".format(timestamp))
            
            # Post the log messages.
            await guild.get_channel(public_mod_channel.id).send(embed=public_log_embed)
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            
            for_incident_log = {
                "incident_type" : "unwarn",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number_warn" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been unwarned within {guild.name}. It was warning #{number}."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            incidents_logs["logs"].append(for_incident_log)
            target["threshold"] -= 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            if successful:
                await ctx.send(f"Dear {author.name}, you have unwarned member {member.name}. I gave them notice of their fate.")
            else:
                await ctx.send(f"Dear {author.name}, you have unwarned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            
            # Save the logs
            await self.config.guild(guild).warn_logs.set(warn_logs)
            await self.config.guild(guild).incidents_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Unwarn **", description=f"**#{number}**\n **Attention.** A user has been unwarned.", color=clr)
            
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})", inline=False)
            log_embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)
            log_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            log_embed.set_footer(text="Date - {}".format(timestamp))
            

            # Post the log messages.
            log_message = await guild.get_channel(modlog_channel.id).send(embed=log_embed)
            
            
            for_incident_log = {
                "incident_type" : "unwarn",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": author.id,
                "staff_name" : author.name, 
                "date" : timestamp,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number_warn" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been unwarned within {guild.name}. It was warning #{number}."
            
            if dm_bool == True:
                try:
                    await member.send(Goodbye)
                    successful = True
                except:
                    successful = False
            else:
                successful = False
            
            incidents_logs["logs"].append(for_incident_log)
            target["threshold"] -= 1
            
            # Manage the threshold, and set the user log back
            await self.threshold_action_hit(ctx, member)
            user_logs[member.id] = target
            
            # Kick the user and send a message.
            if successful:
                await ctx.send(f"Dear {author.name}, you have unwarned member {member.name}. I gave them notice of their fate.")
            else:
                await ctx.send(f"Dear {author.name}, you have unwarned member {member.name}. I could not contact this member and inform them. Either the DM feature is disabled, or I could not contact them.")
            
            # Save the logs
            await self.config.guild(guild).warn_logs.set(warn_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)  
    
    
    
    