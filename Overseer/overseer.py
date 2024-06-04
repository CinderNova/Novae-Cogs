import discord, json, random, asyncio, logging, traceback, redbot.core.data_manager, datetime, re
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from datetime import timedelta
from discord.utils import get

# Set the timestamp as of now.
timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class overseer(commands.Cog):
    """
    Manage all the commands that allow users to express themselves and interact with each other.
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/debug.log"
        self.debug_file = None
        self.identifier = self.bot.user.id
        self.config = Config.get_conf(self, identifier = self.identifier, force_registration=True)
        default_guild = {
            "enable_debug" : False,
            
            "enable_member_blacklist" : False,
            "enable_server_blacklist" : False,
            "enable_member_blacklist_auto_action" : False, 
            
            "enable_verification" : False,
            "enable_verify" : False,
            "enable_entry" : True,
            "enable_verification_log" : True,
            "enable_codeword" : False,
            "enable_instructions" : False,
            "enable_introduction" : False,
            "enable_member_equal_id" : False,
            "enable_dm" : False,
            
            "enable_booster_log" : False,
            "enable_navigation" : False,
            
            "enable_quarantine" : True,
            "enable_public_mod" : True,
            "enable_threshold_action" : False,
            "enable_partner_verification" : False,
            "enable_welcome" : False,
            
            "member_blacklist" : {
                "log" : []},
            "server_blacklist" : {
                "log" : []},
            
            "server_partners" : {},
            "boosting_users" : {},
            
            "users" : {},
            "notes" : {},
    	    "ban_logs" : {},
            "quarantine_logs" : {},
            "kick_logs" : {"logs" : []}, 
            "timeout_logs" : {"logs" : []}, 
            "warn_logs" : {"logs" : []},
            "incident_logs" : {"logs" :[]}, 
            
            "verified_users" : {},
            "crossverified_users" : {},
            
            "entry_ticket_category" : None,
            "welcome_message" : None,
            "codeword_rules" : None,
            "introduction_message" : None,
            "instruction_message" : None,
            
            "member_blacklist_auto_action" : None,
            "threshold_action" : None,
            "warn_threshold" : 5,
            "incident_threshold" : 8,
            
            "quarantine_channel" : None,
            "modlog_channel" : None,
            "log_channel" : None,
            "map_channel" : None,
            "staff_channel" : None,
            "boost_channel" : None,
            "verification_log_channel" : None,
            "partner_verification_channel" : None,
            "welcome_channel" : None,
            "public_moderation_channel" : None,
            
            "member_role" : None,
            "verification_role" : None,
            "booster_role" : None,
            "unverified_role" : None,
            "crossverified_role" : None,
            "staff_role" : None,
            "admin_role" : None,
            "mod_role" : None,
            "freshjoin_role" : None,
            "serverpartner_role" : None,
            "quarantine_role" : None
        }
        self.config.register_guild(**default_guild)


    async def debug_log(self, guild, command, message):
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/{guild.id}-debug.log"
        debug_file = open(debug_file_path, 'a') 
        debug_file.write(f"{datetime.datetime.now()} - Command '{command}': {message}\n")
        debug_file.close()
    
    
    async def threshold_action_hit(self, ctx, member: discord.User):
        """ If a user's warn or incident threshold is reached, they will be banned automatically. """
        
        guild = ctx.guild
        author = ctx.message.author
        target = None
        
        # Get the thresholds
        warn_threshold = await self.config.guild(guild).warn_threshold()
        incident_threshold = await self.config.guild(guild).incident_threshold()
        
        # Get the user, action
        user_log = await self.config.guild(guild).users()
        
        for keys in user_log:
            if user_log[keys]["member_id"] == member.id:
                target = user_log[keys]
        
        if target == None:
            user_log[member.id] = {
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
            target = user_log[member.id]

        action = await self.config.guild(guild).threshold_action()
        # Check if enabled or disabled action, check which action it is
        if not await self.config.guild(guild).enable_threshold_action():
            return
        else:
            if action == "kick":
                reason = f"You have been kicked, as your warn or incident count has reached the threshold. You are intolerable within {guild.name}."
                
                if target["threshold"] >= incident_threshold:
                    try:
                        await member.send(reason)
                        dm_possible=True
                    except:
                        dm_possible = False
                    await guild.kick(member, reason=reason)
                    if dm_possible == True:
                        await ctx.send(f"{member.name} has been kicked from {guild.name}, as their incident count reached the limit. They have been informed.")
                    else:
                        await ctx.send(f"{member.name} has been kicked from {guild.name}, as their incident count reached the limit. They have been informed.")
                    target["threshold"] = 0
                elif len(target["warns"]) >= warn_threshold:
                    try:
                        await member.send(reason)
                        dm_possible=True
                    except:
                        dm_possible = False
                    await guild.kick(member, reason=reason)
                    if dm_possible == True:
                        await ctx.send(f"{member.name} has been kicked from {guild.name}, as their warn count reached the limit. They have been informed.")
                    else:
                        await ctx.send(f"{member.name} has been kicked from {guild.name}, as their warn count reached the limit. They have been informed.")
                    target["threshold"] = 0
            elif action == "ban":
                reason = f"You have been banned, as your warn or incident count has reached the threshold. You are intolerable within {guild.name}."
                
                if target["threshold"] >= incident_threshold:
                    try:
                        await member.send(reason)
                        dm_possible=True
                    except:
                        dm_possible = False
                    await guild.kick(member, reason=reason)
                    if dm_possible == True:
                        await ctx.send(f"{member.name} has been banned from {guild.name}, as their incident count reached the limit. They have been informed.")
                    else:
                        await ctx.send(f"{member.name} has been banned from {guild.name}, as their incident count reached the limit. They have been informed.")
                    target["threshold"] = 0
                elif len(target["warns"]) >= warn_threshold:
                    try:
                        await member.send(reason)
                        dm_possible=True
                    except:
                        dm_possible = False
                    await guild.kick(member, reason=reason)
                    if dm_possible == True:
                        await ctx.send(f"{member.name} has been banned from {guild.name}, as their warn count reached the limit. They have been informed.")
                    else:
                        await ctx.send(f"{member.name} has been banned from {guild.name}, as their warn count reached the limit. They have been informed.")
                    target["threshold"] = 0
            elif action == None:
                return
      
    @commands.Cog.listener()
    async def on_message(self, message):
        
        """ Implement the channel searching function. """
        guild = message.guild
        channe = message.channel
        if message.content.startswith(f"Themis,") and await self.config.guild(guild).enable_nagivation():
        
            author = message.author
            if message.content.startswith('Themis, fetch me') and message.content.endswith(' please.'):
                chlist = []
                msg_1 = re.sub('Themis, fetch me ', '', message.content)
                msg = re.sub(', please.', '', msg_1)
                for channel in guild.channels:
                    if channel.name[2:] in msg.lower():
                        chlist.append(channel)
                await asyncio.sleep(1)
                
                if chlist == []:
                    await guild.get_channel(channe.id).send(f"My apologies, {author.name}, these channels do not exist, currently.")
                else:
                    it = f"Dear {author.name}, I have found the following channels: "
                    for el in chlist:
                        it+= f"{el.mention} "
                    await guild.get_channel(channe.id).send(it)

                        
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        """ Check for blacklisted member joins. """
        
        guild = member.guild
        clr = 0xF96161
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        target = None
        
        channel = get(guild.channels, id=await self.config.guild(guild).staff_channel())
        staffrole = get(guild.roles, id= await self.config.guild(guild).staff_role())
        modlog = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        quarantinerole = get(guild.roles, id = await self.config.guild(guild).quarantine_role())
        if channel == None or staffrole == None or modlog == None or quarantinerole == None:
            return
        
        if not await self.config.guild(guild.id).enable_member_blacklist_auto_action():
            return
        
        action = await self.config.guild(guild.id).member_blacklist_auto_action()
        if action == None or action.lower() not in ["kick", "ban", "quarantine", "alert"]:
            return
        elif action.lower() == "kick":
            blacklist = await self.config.guild(guild).member_blacklist()
            b_log = blacklist["logs"]
            is_in = False
            for items in b_log:
                if items["member_id"] == member.id:
                    is_in = True
                    target = items
            
            if is_in == False:
                return
            
            content = target["reason"]
            
            embed = discord.Embed(title="** Kick has been issued. **", description=f"**A blacklisted Member has joined the server!** \n As the blacklist auto action has been set to 'kick', I will proceed to ping the Staff. \nThe following user, that is blacklisted, joined:", color=clr)
            embed.add_field(name=f"**User:**", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name=f"**Reason:**", value=f"{content}", inline=False)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            # Get user, make sure there is existing log
            kick_log = await self.config.guild(guild).ban_logs()
            kick_logs = kick_log["logs"]
            incidents_logs = await self.config.guild(guild).incident_logs()
            user_logs = await self.config.guild(guild).users()
            target = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target = user_logs[keys]
            
            for logs in kick_logs:
                if logs["member_id"] == member.id:
                    logged_already = logs
                    return

            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Kick **", description=f"**Attention.** A user has been kicked in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=content)
            log_embed.add_field(name="**by Staff**", value=f"Themis Auto Action", inline=False)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.set_footer(text="Date - {}".format(timestamp))

            
            
            # Post the log messages.
            log_message = await guild.get_channel(modlog.id).send(embed=embed)
            
            number = len(target["kicks"]) + 1
            
            for_kick_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "kick",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed suspicious or otherwise worthy of investigation within {guild.name} for your behaviour, thus you were kicked.\n My deepest apologies."
            
            try:
                await member.send(Goodbye)
                successful = True
            except:
                successful = False
            
            kick_logs["logs"][member.id] = for_kick_log
            incidents_logs["logs"].append(for_incident_log)
            target["kicks"].append(for_kick_log)
            target["threshold"] += 1
            
            user_logs[member.id] = target
            
            # Quarantine the user or send a message.
            try: 
                await guild.ban(member, reason=f"My apologies, you have been deemed unworthy of {guild.name}.")
            except:
                await guild.get_channel(channel.id).send(f"My apologies, however, I was not able to kick {member.name} ({member.mention}). There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).kick_logs.set(kick_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        
            await guild.get_channel(channel.id).send(embed=embed)
            await guild.get_channel(channel.id).send(f"||{staffrole.mention}||") 
        elif action.lower() == "ban":
            blacklist = await self.config.guild(guild).member_blacklist()
            b_log = blacklist["logs"]
            is_in = False
            for items in b_log:
                if items["member_id"] == member.id:
                    is_in = True
                    target = items
            
            if is_in == False:
                return
            
            content = target["reason"]
            
            embed = discord.Embed(title="** Ban has been issued. **", description=f"**A blacklisted Member has joined the server!** \n As the blacklist auto action has been set to 'ban', I will proceed to ping the Staff. \nThe following user, that is blacklisted, joined:", color=clr)
            embed.add_field(name=f"**User:**", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name=f"**Reason:**", value=f"{content}", inline=False)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            # Get user, make sure there is existing log
            ban_logs = await self.config.guild(guild).ban_logs()
            incidents_logs = await self.config.guild(guild).incident_logs()
            user_logs = await self.config.guild(guild).users()
            target = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target = user_logs[keys]
            
            for logs in ban_logs:
                if logs["member_id"] == member.id:
                    logged_already = logs
                    return
                    
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Ban **", description=f"**Attention.** A user has been banned in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=content)
            log_embed.add_field(name="**by Staff**", value=f"Themis Auto Action", inline=False)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.set_footer(text="Date - {}".format(timestamp))

            
            # Post the log messages.
            log_message = await guild.get_channel(modlog.id).send(embed=log_embed)
            
            number = len(target["bans"]) + 1
            
            for_ban_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "ban",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed suspicious or otherwise worthy of investigation within {guild.name} for your behaviour, thus you were banned.\n My deepest apologies."
            
            try:
                await member.send(Goodbye)
                successful = True
            except:
                successful = False
            
            ban_logs[member.id] = for_ban_log
            incidents_logs["logs"].append(for_incident_log)
            target["bans"].append(for_ban_log)
            target["threshold"] += 1
            
            user_logs[member.id] = target
            
            # Quarantine the user or send a message.
            try: 
                await guild.ban(member, reason=f"My apologies, you have been deemed unworthy of {guild.name}.")
            except:
                await guild.get_channel(channel.id).send(f"My apologies, however, I was not able to ban {member.name} ({member.mention}). There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).ban_logs.set(ban_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        
            await guild.get_channel(channel.id).send(embed=embed)
            await guild.get_channel(channel.id).send(f"||{staffrole.mention}||") 
        elif action.lower() == "quarantine":
            
            
            
            blacklist = await self.config.guild(guild).member_blacklist()
            b_log = blacklist["logs"]
            is_in = False
            for items in b_log:
                if items["member_id"] == member.id:
                    is_in = True
                    target = items
            
            if is_in == False:
                return
            
            content = target["reason"]
            
            embed = discord.Embed(title="** Quarantine has been issued. **", description=f"**A blacklisted Member has joined the server!** \n As the blacklist auto action has been set to 'quarantine', I will proceed to ping the Staff. \nThe following user, that is blacklisted, joined:", color=clr)
            embed.add_field(name=f"**User:**", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name=f"**Reason:**", value=f"{content}", inline=False)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            # Get user, make sure there is existing log
            quarantine_logs = await self.config.guild(guild).quarantine_logs()
            incidents_logs = await self.config.guild(guild).incident_logs()
            user_logs = await self.config.guild(guild).users()
            target = None
            logged_already = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target = user_logs[keys]
            
            for logs in quarantine_logs:
                if logs["member_id"] == member.id:
                    logged_already = logs
            
            if logged_already != None and quarantinerole in member.roles:
                await guild.get_channel(channel.id).send("This user is already quarantined.")

        

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

            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Quarantine **", description=f"**Attention.** A user has been quarantined in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=content)
            log_embed.add_field(name="**by Staff**", value=f"Themis Auto Action", inline=False)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.set_footer(text="Date - {}".format(timestamp))

            
            # Post the log messages.
            log_message = await guild.get_channel(modlog.id).send(embed=log_embed)
            
            temp_list_roles = []
            for rls in member.roles:
                temp_list_roles.append(rls.id)
            
            number = len(target["quarantines"]) + 1
            
            for_quarantine_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "quarantine",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "roles" : temp_list_roles,
                "number" : number
            }

            Goodbye = f"Attention, {member.mention}, \n you have been deemed suspicious or otherwise worthy of investigation within {guild.name} for your behaviour, thus you were quarantined.\n My deepest apologies."
            
            try:
                await member.send(Goodbye)
                successful = True
            except:
                successful = False
            
            quarantine_logs[member.id] = for_quarantine_log
            incidents_logs["logs"].append(for_incident_log)
            target["quarantines"].append(for_quarantine_log)
            target["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            user_logs[member.id] = target
            
            # Quarantine the user or send a message.
            try: 
                await member.edit(roles=[quarantinerole])
            except:
                await guild.get_channel(channel.id).send(f"My apologies, however, I was not able to quarantine {member.name} ({member.mention}). There has been an error. Please attempt again, and contact my Creator.")
                return
            
            # Save the logs
            await self.config.guild(guild).quarantine_logs.set(quarantine_logs)
            await self.config.guild(guild).incident_logs.set(incidents_logs)
            await self.config.guild(guild).users.set(user_logs)     
        
            await guild.get_channel(channel.id).send(embed=embed)
            await guild.get_channel(channel.id).send(f"||{staffrole.mention}||")
        elif action.lower() == "alert":
            
            blacklist = await self.config.guild(guild).member_blacklist()
            b_log = blacklist["logs"]
            is_in = False
            for items in b_log:
                if items["member_id"] == member.id:
                    is_in = True
                    target = items
            
            if is_in == False:
                return
            
            content = target["reason"]
            
            embed = discord.Embed(title="** Alert has been issued. **", description=f"**A blacklisted Member has joined the server!** \n As the blacklist auto action has been set to 'alert', I will proceed to ping the Staff. \nThe following user, that is blacklisted, joined:", color=clr)
            embed.add_field(name=f"**User:**", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name=f"**Reason:**", value=f"{content}", inline=False)
            embed.set_footer(text="Date - {}".format(timestamp))
            await guild.get_channel(channel.id).send(embed=embed)
            await guild.get_channel(channel.id).send(f"||{staffrole.mention}||")
        
    @commands.Cog.listener()
    async def on_member_update(self, member: discord.Member):
        
        """ Check if a member is boosting. """
        guild = member.guild
        boost_list = await self.config.guild(guild).boosting_users()
        boost_role = get(guild.roles,id= await self.config.guild(guild).booster_role())
        dummy = False
        if boost_role == None:
            return
        
        if boost_role in member.roles:
            
            if boost_list != {}:
                for keys in boost_list:
                    if boost_list[keys]["user_id"] == member.id:
                        dummy = True
                
            
            if dummy == False:
                boost_list[member.id] = {
                    "user_id" : member.id,
                    "user_name" : member.name,
                    "date" : timestamp,
                    "custom_role" : "None.",
                    "custom_colour" : "None.",
                    "custom_name" : "None."
                }
            
            
        
        
                    

                
        
        
        
        
        
    
    
    
    # OVERARCHING CATEGORIES
    
    @commands.group(name="partners")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def partners(self, ctx):
        
        """ Family of commands relating to partner servers. This includes adding, removing, showing and managing (reasons, managers, verification roles) of partner servers. """
    
    @commands.group(name="moderation")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def moderation(self, ctx):
        """ The group of commands related to moderation settings. """
    
    @commands.group(name="verification")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def verification(self, ctx):
        """ The group of commands related to verification settings. """
    
    @commands.group(name="overseer")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def overseer(self, ctx):
        """ The group of commands related to more general settings. """
    
    @overseer.group(name="settings")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """ The group of commands related to managing the settings of moderation and verification. """
    
    @settings.group(name="channel")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def channel(self, ctx):
        """ The group of commands related to managing the channels. """
        
    @settings.group(name="role")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx):
        """ The group of commands related to managing the role. """
    
    @settings.group(name="blacklists")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def blacklists(self, ctx):
        """ The group of commands related to managing the blacklist. """
    
    @blacklists.group(name="member")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def member(self, ctx):
        """ The group of commands related to managing the member blacklist. """
        
    @blacklists.group(name="server")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def server(self, ctx):
        """ The group of commands related to managing the server blacklist. """
    
    @overseer.group(name="bools")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def bools(self, ctx):
        """ The group of commands related to managing the bools. """
    

    
    # BOOLEANS
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_boosterlog(self, ctx, bools: str):
        """ Enable or disable logging boosting members. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_booster_log' sub-command of 'moderation' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_booster_log.set(True)
            await ctx.send("You have successfully enabled the booster log feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_booster_log.set(False)
            await ctx.send("You have successfully disabled the booster log feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_dm(self, ctx, bools: str):
        """ Enable or disable the bot being able to DM members for staff-related actioning. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_dm' sub-command of 'bools' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_dm.set(True)
            await ctx.send("You have successfully enabled the DM feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_dm.set(False)
            await ctx.send("You have successfully disabled the DM feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_member_equal_id(self, ctx, bools: str):
        """ Enable or disable member being the same as the ID-verified role. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_member_equal_id' sub-command of 'overseer bools' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_member_equal_id.set(True)
            await ctx.send("You have successfully enabled member = ID-verified option.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_member_equal_id.set(False)
            await ctx.send("You have successfully disabled the member = ID-verified option.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_member_blacklist(self, ctx, bools: str):
        """ Enable or disable the member blacklist. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_member_blacklist' sub-command of 'moderation' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_member_blacklist.set(True)
            await ctx.send("You have successfully enabled the member blacklist feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_member_blacklist.set(False)
            await ctx.send("You have successfully disabled the member blacklist feature.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_member_blacklist_auto_action(self, ctx, bools: str):
        """ Enable or disable the member blacklist auto action. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_member_blacklist_auto_action' sub-command of 'moderation' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_member_blacklist_auto_action.set(True)
            await ctx.send("You have successfully enabled the member blacklist auto action.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_member_blacklist_auto_action.set(False)
            await ctx.send("You have successfully disabled the member blacklist auto action.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_server_blacklist(self, ctx, bools: str):
        """ Enable or disable the server blacklist. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_server_blacklist' sub-command of 'moderation' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_server_blacklist.set(True)
            await ctx.send("You have successfully enabled the server blacklist feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_server_blacklist.set(False)
            await ctx.send("You have successfully disabled the server blacklist feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_debug(self, ctx, bools: str):
        """Enable or disable debugging."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_debug.set(True)
            await ctx.send("You have successfully enabled debugging.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_debug.set(False)
            await ctx.send("You have successfully disabled debugging.")
        else:
            await ctx.send("Enter either true or false.")
            
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_navigation(self, ctx, bools: str):
        """Enable or disable the map / navigation."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_navigation' sub-command of 'overseer' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_navigation.set(True)
            await ctx.send("You have successfully enabled navigation.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_navigation.set(False)
            await ctx.send("You have successfully disabled navigation.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_verification(self, ctx, bools: str):
        """ Enable or disable verification. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_verification' sub-command of 'verification' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_verification.set(True)
            await ctx.send("You have successfully enabled the verification feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_verification.set(False)
            await ctx.send("You have successfully disabled the verification feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_verify(self, ctx, bools: str):
        """ Enable or disable stage one verification. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_verify' sub-command of 'verification' command.")
            return

        # Enable or disable verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_verify.set(True)
            await ctx.send("You have successfully enabled the stage 1 verification feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_verify.set(False)
            await ctx.send("You have successfully disabled the stage 1 verification feature.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_introduction(self, ctx, bools: str):
        """ Enable or disable the introduction. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_introduction' sub-command of 'verification' command.")
            return

        # Enable or disable verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_introduction.set(True)
            await ctx.send("You have successfully enabled the introduction feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_introduction.set(False)
            await ctx.send("You have successfully disabled the introduction feature.")
        else:
            await ctx.send("Enter either true or false.")
            
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_partner_verification(self, ctx, bools: str):
        """ Enable or disable the partner verification log. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_partner_verification' sub-command of 'verification' command.")
            return

        # Enable or disable verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_partner_verification.set(True)
            await ctx.send("You have successfully enabled the partner verification log feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_partner_verification.set(False)
            await ctx.send("You have successfully disabled the partner verification log feature.")
        else:
            await ctx.send("Enter either true or false.")
            
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_welcome(self, ctx, bools: str):
        """ Enable or disable the welcome upon verifying. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_welcome' sub-command of 'verification' command.")
            return

        # Enable or disable verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_welcome.set(True)
            await ctx.send("You have successfully enabled the welcome feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_welcome.set(False)
            await ctx.send("You have successfully disabled the welcome feature.")
        else:
            await ctx.send("Enter either true or false.")
            
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_instructions(self, ctx, bools: str):
        """ Enable or disable instructions. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_instructions' sub-command of 'verification' command.")
            return

        # Enable or disable verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_instructions.set(True)
            await ctx.send("You have successfully enabled the instruction feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_instructions.set(False)
            await ctx.send("You have successfully disabled the instruction feature.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_entry(self, ctx, bools: str):
        """ Enable or disable entry (stage 2) verification. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_entry' sub-command of 'verification' command.")
            return

        # Enable or disable entry verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_entry.set(True)
            await ctx.send("You have successfully enabled stage 2 verification.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_entry.set(False)
            await ctx.send("You have successfully disabled stage 2 verification.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_verificationlog(self, ctx, bools: str):
        """ Enable or disable the verification log. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_verificationlog' sub-command of 'verification' command.")
            return

        # Enable or disable verification log and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_verification_log.set(True)
            await ctx.send("You have successfully enabled the verification logging feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_verification_log.set(False)
            await ctx.send("You have successfully disabled the verification logging feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_public_mod(self, ctx, bools: str):
        """ Enable or disable the public moderation log. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_public_mod' sub-command of 'moderation' command.")
            return

        # Enable or disable verification log and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_public_mod.set(True)
            await ctx.send("You have successfully enabled the public moderation logging feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_public_mod.set(False)
            await ctx.send("You have successfully disabled the public moderation logging feature.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_threshold_action(self, ctx, bools: str):
        """ Enable or disable the threshold action. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_threshold_action' sub-command of 'moderation' command.")
            return

        # Enable or disable verification log and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_threshold_action.set(True)
            await ctx.send("You have successfully enabled the threshold action feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_threshold_action.set(False)
            await ctx.send("You have successfully disabled the threshold action feature.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_quarantine(self, ctx, bools: str):
        """ Enable or disable quarantine. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_quarantine' sub-command of 'moderation' command.")
            return

        # Enable or disable verification log and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_quarantine.set(True)
            await ctx.send("You have successfully enabled the quarantine feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_quarantine.set(False)
            await ctx.send("You have successfully disabled the quarantine feature.")
        else:
            await ctx.send("Enter either true or false.")

    @bools.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_codeword(self, ctx, bools: str):
        """ Enable or disable the codeword. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_codeword' sub-command of 'verification' command.")
            return

        # Enable or disable entry verification and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_codeword.set(True)
            await ctx.send("You have successfully enabled the codeword.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_codeword.set(False)
            await ctx.send("You have successfully disabled the codeword.")
        else:
            await ctx.send("Enter either true or false.")



    
    # SET THE ENTRY TICKET CATEGORY, AUTO ACTION, ...
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def entry_category(self, ctx, entry_ticket_category: discord.CategoryChannel):
        
        """ Set the ticket entry category for the auto-ticket service. """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'entry_category' sub-command of 'verification entry_category' command.")
            return
        
        await self.config.guild(guild).entry_ticket_category.set(entry_ticket_category.id)
        await ctx.send(f"You have successfully set the entry category for tickets to '{entry_ticket_category.name}'.")
        
    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def auto_action(self, ctx, action: str):
        
        """ Set the auto action for blacklisted members.  """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'auto_action' sub-command of 'overseer settings blacklists member' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if action.lower() in ["kicks", "kick", "kicking", "kicked"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("kick")
            await ctx.send(f"You have successfully set the member blacklist auto action to 'kick'.")
        elif action.lower() in ["bans", "ban", "banning", "banned"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("ban")
            await ctx.send(f"You have successfully set the member blacklist auto action to 'ban'.")
        elif action.lower() in ["alert", "alerts", "alerting", "warning"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("alert")
            await ctx.send(f"You have successfully set the member blacklist auto action to 'alert'. This will alert the staff only.")
        elif action.lower() in ["quarantines", "quarantine", "quarantineing", "quarantined"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("ban")
            await ctx.send(f"You have successfully set the member blacklist auto action to 'ban'.")
        else:
            await ctx.send(f"You have not set the member blacklist auto action, since the input is not recognised as an option. The available options are 'ban', 'kick', 'quarantine', and 'alert'.")
            return
 
        
        
        
    # SET THE CHANNELS
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def quarantine_channel(self, ctx, quarantine_channel: discord.TextChannel):
        """ Set the quarantine channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'quarantine' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).quarantine_channel.set(quarantine_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the quarantine channel to {quarantine_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def modlog(self, ctx, modlog_channel: discord.TextChannel):
        """ Set the Modlog channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'modlog' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).modlog_channel.set(modlog_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the modlog channel to {modlog_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def log_channel(self, ctx, log_channel: discord.TextChannel):
        """ Set the log channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'log' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).log_channel.set(log_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the log channel to {log_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def map(self, ctx, map_channel: discord.TextChannel):
        """ Set the map / navigation channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'map' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).map_channel.set(map_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the navigation channel to {map_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def staff_channel(self, ctx, staff_channel: discord.TextChannel):
        """ Set the staff channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'staff' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).staff_channel.set(staff_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the staff channel to {staff_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def boost(self, ctx, boost_channel: discord.TextChannel):
        """ Set the boost channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'boost' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).boost_channel.set(boost_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the boost channel to {boost_channel.mention}, {author.name}.")
        
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def verification_log(self, ctx, verification_channel: discord.TextChannel):
        """ Set the verification log channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'verification_log' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).verification_log_channel.set(verification_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the verification log channel to {verification_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def partner_verification(self, ctx, partner_verification_channel: discord.TextChannel):
        """ Set the partner verification channel (partner servers can see verifications). """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'partner_verification' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).partner_verification_channel.set(partner_verification_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the partner verification channel to {partner_verification_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def welcome(self, ctx, welcome_channel: discord.TextChannel):
        """ Set the welcome channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'welcome' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).welcome_channel.set(welcome_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the welcome channel to {welcome_channel.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def public_moderation(self, ctx, public_moderation_channel: discord.TextChannel):
        """ Set the public moderation channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'public_moderation' sub-command of 'overseer settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).public_moderation_channel.set(public_moderation_channel.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the public moderation channel to {public_moderation_channel.mention}, {author.name}.")
    
    
    
    # SET THE ROLES
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def memberrole(self, ctx, member_role: discord.Role):
        """ Set the member (ID-verified) role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'member' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).member_role.set(member_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the member role to {member_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def booster(self, ctx, booster_role: discord.Role):
        """ Set the server booster role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'booster' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).booster_role.set(booster_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the booster role to {booster_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unverified(self, ctx, unverified_role: discord.Role):
        """ Set the unverified role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'unverified' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).unverified_role.set(unverified_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the unverified role to {unverified_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def crossverified(self, ctx, crossverified_role: discord.Role):
        """ Set the crossverified role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'crossverified' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).crossverified_role.set(crossverified_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the crossverified role to {crossverified_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def staff(self, ctx, staff_role: discord.Role):
        """ Set the staff role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'staff' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).staff_role.set(staff_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the staff role to {staff_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def admin(self, ctx, admin_role: discord.Role):
        """ Set the admin role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'admin' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).admin_role.set(admin_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the admin role to {admin_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def mod(self, ctx, mod_role: discord.Role):
        """ Set the mod role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'mod' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).mod_role.set(mod_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the mod role to {mod_role.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def id_role(self, ctx, id_role: discord.Role):
        """ Set the ID-verified role. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'id_role' sub-command of 'overseer settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).verification_role.set(id_role.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the verification role to {id_role.mention}, {author.name}.")
    
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def freshjoin(self, ctx, freshjoin_role: discord.Role):
        """ Set the role users get upon joining the server first. """
    
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'freshjoin' sub-command of 'overseer settings role' command.")
            return
    
        # Set the freshjoin role.
        await self.config.guild(guild).freshjoin_role.set(freshjoin_role.id)
    
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the freshjoin role to {freshjoin_role.mention}, {author.name}.")

    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def serverpartner(self, ctx, serverpartner_role: discord.Role):
        """ Set the server partner role. """
    
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'serverpartner' sub-command of 'overseer settings role' command.")
            return
    
        # Set the serverpartner role.
        await self.config.guild(guild).serverpartner_role.set(serverpartner_role.id)
    
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the serverpartner role to {serverpartner_role.mention}, {author.name}.")

    @role.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def quarantinerole(self, ctx, quarantine_role: discord.Role):
        """ Set the quarantine role. """
    
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'quarantine' sub-command of 'overseer settings role' command.")
            return
    
        # Set the quarantine role.
        await self.config.guild(guild).quarantine_role.set(quarantine_role.id)
    
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the quarantine role to {quarantine_role.mention}, {author.name}.")


    
    # THRESHOLDS AND OTHER SETTINGS
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def warn_threshold(self, ctx, threshold: int):
        """ Set the warning threshold. Once a member reaches the threshold, they will be automatically kicked. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        if threshold == 0 or threshold < 0:
            await ctx.send(f"My apologies, {author.name}, however, the warning threshold needs to be higher than zero and a positive number. Please set an integer higher than 0.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'warn_threshold' sub-command of 'moderation' command.")
            return
        
        await self.config.guild(guild).warn_threshold.set(threshold)
        await ctx.send(f"You have successfully set the warning threshold to {threshold}.")
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def incident_threshold(self, ctx, threshold: int):
        """ Set the incident threshold. Once a member reaches the threshold, they will be automatically kicked. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        if threshold == 0 or threshold < 0:
            await ctx.send(f"My apologies, {author.name}, however, the threshold needs to be higher than zero and a positive number. Please set an integer higher than 0.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'incident_threshold' sub-command of 'moderation' command.")
            return
        
        await self.config.guild(guild).incidents_threshold.set(threshold)
        await ctx.send(f"You have successfully set the incident threshold to {threshold}.")
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def threshold_action(self, ctx, threshold_action: str=None):
        """ Set the threshold action. Once a member reaches the threshold, this action will determine their fate. Leave empty if you want nothing to happen."""
        guild = ctx.guild
        author = ctx.message.author
        
        if threshold_action.lower() in ["kick", "kicking", "kicked", "kicks"]:
            await self.config.guild(guild).threshold_action.set("kick")
            await ctx.send(f"You have successfully set the threshold action to {threshold_action}. Users reaching the threshold will now be kicked.")
        elif threshold_action.lower() in ["ban", "banning", "banned", "bans"]:
            await self.config.guild(guild).threshold_action.set("ban")
            await ctx.send(f"You have successfully set the threshold action to {threshold_action}. Users reaching the threshold will now be banned.")
        elif threshold_action.lower() in ["none", "nothing", None, ""]:
            await self.config.guild(guild).threshold_action.set(None)
            await ctx.send(f"You have successfully set the threshold action to {threshold_action}. Nothing will happen once users reach the threshold.")
        else:
            await ctx.send(f"My apologies, {author.name}, however, you need to set a specific action. You can choose from ban, kick and none.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'threshold_action' sub-command of 'moderation' command.")
            return

    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self, ctx, *, welcome_message: str):
        """ Set the welcome message. This message will be sent into the [welcome] channel previously set to greet a user upon *verifying*. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'welcome_message' sub-command of 'verification' command.")
            return
        
        await self.config.guild(guild).welcome_message.set(welcome_message)
        await ctx.send(f"You have successfully set the welcome message to: \n{welcome_message}")
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def set_codeword(self, ctx, *, codeword: str):
        """ Set the codeword hidden in the rules. This codeword is required for users to enter in the ticket (with /codeword (..)). """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'codeword' sub-command of 'verification' command.")
            return
        
        await self.config.guild(guild).codeword_rules.set(codeword)
        await ctx.send(f"You have successfully set the codeword to: \n{codeword}")
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def introduction(self, ctx, *, introduction: str=None):
        """ Set the introduction template required (if any). Leave empty otherwise. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'introduction' sub-command of 'verification' command.")
            return
        
        if introduction == None:
            introduction_ = "None set."
        else:
            introduction_ = introduction
        
        await self.config.guild(guild).introduction_message.set(introduction_)
        await ctx.send(f"You have successfully set the introduction template to: \n{introduction_}")
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def instruction_message(self, ctx, *, instructions: str):
        """ Set the instructions that will be sent into the ticket upon giving the correct codeword. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'instruction_message' sub-command of 'verification' command.")
            return
        
        await self.config.guild(guild).instruction_message.set(instructions)
        await ctx.send(f"You have successfully set the instruction message to \n{instructions}")



    # VIEW THE SETTINGS
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def show_settings(self, ctx):
        
        """ View the settings for the Overseer Aspect. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        all_embeds = []
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'show_settings' sub-command of 'overseer settings' command.")
            return
        
        # Collect all the booleans
        booster_log_bool = await self.config.guild(guild).enable_booster_log()
        member_blacklist_bool = await self.config.guild(guild).enable_member_blacklist()
        member_blacklist_auto_action_bool = await self.config.guild(guild).enable_member_blacklist_auto_action()
        server_blacklist_bool = await self.config.guild(guild).enable_server_blacklist()
        debug_bool = await self.config.guild(guild).enable_debug()
        navigation_bool = await self.config.guild(guild).enable_navigation()
        verification_bool = await self.config.guild(guild).enable_verification()
        verify_bool = await self.config.guild(guild).enable_verify()
        introduction_bool = await self.config.guild(guild).enable_introduction()
        partner_verification_bool = await self.config.guild(guild).enable_introduction()
        welcome_bool = await self.config.guild(guild).enable_welcome()
        instructions_bool = await self.config.guild(guild).enable_instructions()
        entry_bool = await self.config.guild(guild).enable_entry()
        verification_log_bool = await self.config.guild(guild).enable_verification_log()
        public_mod_bool = await self.config.guild(guild).enable_public_mod()
        threshold_bool = await self.config.guild(guild).enable_threshold_action()
        quarantine_bool = await self.config.guild(guild).enable_quarantine()
        codeword_bool = await self.config.guild(guild).enable_codeword()
        member_equal_id_bool = await self.config.guild(guild).enable_member_equal_id()
        dm_bool = await self.config.guild(guild).enable_dm()
        
        
        # Collect Misc.
        
        if await self.config.guild(guild).member_blacklist_auto_action() != None:
            member_auto_action = await self.config.guild(guild).member_blacklist_auto_action()
        else:
            member_auto_action = "Not set."
            
        if await self.config.guild(guild).warn_threshold() != None:
            warn_threshold = await self.config.guild(guild).warn_threshold() 
        else:
            warn_threshold = "Not set."
            
        if await self.config.guild(guild).incident_threshold() != None:
            incident_threshold = await self.config.guild(guild).incident_threshold()
        else:
            incident_threshold = "Not set."
            
        if await self.config.guild(guild).threshold_action() != None:
            threshold_action = await self.config.guild(guild).threshold_action()
        else:
            threshold_action = "Not set."
            
        if await self.config.guild(guild).welcome_message() != None:
            welcome_message = await self.config.guild(guild).welcome_message()
        else:
            welcome_message = "Not set."
            
        if await self.config.guild(guild).introduction_message() != None:
            introduction = await self.config.guild(guild).introduction_message()
        else:
            introduction = "Not set."
            
        if await self.config.guild(guild).instruction_message() != None:
            instruction = await self.config.guild(guild).instruction_message()
        else: 
            instruction = "Not set."
        
        if await self.config.guild(guild).codeword_rules() != None:
            codeword = await self.config.guild(guild).codeword_rules()
        else:
            codeword = "Not set."
        
        # Collect all roles.
        
        try:
            staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
            staff_role = staff_role.mention
        except:
            staff_role = "Not set."
        
        try:
            member_role = get(guild.roles, id=await self.config.guild(guild).member_role())
            member_role = member_role.mention
        except:
            member_role = "Not set."

        try:
            id_role = get(guild.roles, id=await self.config.guild(guild).verification_role())
            id_role = id_role.mention
        except:
            id_role = "Not set."
        
        try:
            booster_role = get(guild.roles, id=await self.config.guild(guild).booster_role())
            booster_role = booster_role.mention
        except:
            booster_role = "Not set."

        try:
            unverified_role = get(guild.roles, id=await self.config.guild(guild).unverified_role())
            unverified_role = unverified_role.mention
        except:
            unverified_role = "Not set."

        try:
            crossverified_role = get(guild.roles, id=await self.config.guild(guild).crossverified_role())
            crossverified_role = crossverified_role.mention
        except:
            crossverified_role = "Not set."

        try:
            freshjoin_role = get(guild.roles, id=await self.config.guild(guild).freshjoin_role())
            freshjoin_role = freshjoin_role.mention
        except:
            freshjoin_role = "Not set."

        try:
            serverpartner_role = get(guild.roles, id=await self.config.guild(guild).serverpartner_role())
            serverpartner_role = serverpartner_role.mention
        except:
            serverpartner_role = "Not set."

        try:
            quarantine_role = get(guild.roles, id=await self.config.guild(guild).quarantine_role())
            quarantine_role = quarantine_role.mention
        except:
            quarantine_role = "Not set."

        try:
            admin_role = get(guild.roles, id=await self.config.guild(guild).admin_role())
            admin_role = admin_role.mention
        except:
            admin_role = "Not set."

        try:
            mod_role = get(guild.roles, id=await self.config.guild(guild).mod_role())
            mod_role = mod_role.mention
        except:
            mod_role = "Not set."

        
        # Collect all the channels
        
        try:
            entry_category= get(guild.channels, id=await self.config.guild(guild).entry_ticket_category())
            entry_category_channel = entry_category.name
        except:
            entry_category_channel = "Not set."
            
        try:
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())
            log_channel = log_channel.mention
        except:
            log_channel = "Not set."
        
        try:
            quarantine_channel = get(guild.channels, id=await self.config.guild(guild).quarantine_channel())
            quarantine_channel = quarantine_channel.mention
        except:
            quarantine_channel = "Not set."

        try:
            modlog_channel = get(guild.channels, id=await self.config.guild(guild).modlog_channel())
            modlog_channel = modlog_channel.mention
        except:
            modlog_channel = "Not set."

        try:
            map_channel = get(guild.channels, id=await self.config.guild(guild).map_channel())
            map_channel = map_channel.mention
        except:
            map_channel = "Not set."

        try:
            staff_channel = get(guild.channels, id=await self.config.guild(guild).staff_channel())
            staff_channel = staff_channel.mention
        except:
            staff_channel = "Not set."

        try:
            boost_channel = get(guild.channels, id=await self.config.guild(guild).boost_channel())
            boost_channel = boost_channel.mention
        except:
            boost_channel = "Not set."

        try:
            verification_log_channel = get(guild.channels, id=await self.config.guild(guild).verification_log_channel())
            verification_log_channel = verification_log_channel.mention
        except:
            verification_log_channel = "Not set."

        try:
            partner_verification_channel = get(guild.channels, id=await self.config.guild(guild).partner_verification_channel())
            partner_verification_channel = partner_verification_channel.mention
        except:
            partner_verification_channel = "Not set."

        try:
            welcome_channel = get(guild.channels, id=await self.config.guild(guild).welcome_channel())
            welcome_channel = welcome_channel.mention
        except:
            welcome_channel = "Not set."

        try:
            public_moderation_channel = get(guild.channels, id=await self.config.guild(guild).public_moderation_channel())
            public_moderation_channel = public_moderation_channel.mention
        except:
            public_moderation_channel = "Not set."

        
        # Main Page
        main = "You can use the emojis below to navigate the settings. \nPage 2 of 5 will detail all the enabled or disabled settings.\nPage 3 of 5 will show you Moderation Aspect of Overseer. \nPage 4 of 5 will show you the a part of the Verification Aspect of Overseer. \nPage 5 of 5 will show the rest."
        main_embed = discord.Embed(title="**Overseer Settings**", description="**Main Page**: \n" + main, color=clr)
        main_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        main_embed.add_field(name="Date", value="{}".format(timestamp))
        main_embed.set_footer(text="Page    1 / 5")
        all_embeds.append(main_embed)
        
        # Boolean: All enabled / disabled settings
        bools = f"**Enable Debug:** {debug_bool} \n**Enable Navigation:** {navigation_bool} \n**Enable DM for Staff-Action:** {dm_bool} \n**Enable Booster Log:** {booster_log_bool} \n**Enable Public Moderation:** {public_mod_bool} \n**Enable Quarantine:** {quarantine_bool} \n**Enable Threshold:** {threshold_bool} \n**Enable Member Blacklist:** {member_blacklist_bool} \n**Enable Member Blacklist Auto Action:** {member_blacklist_auto_action_bool} \n**Enable Server Blacklist:** {server_blacklist_bool} \n**Enable Verification:** {verification_bool} \n**Enable Member = ID-Verified:** {member_equal_id_bool} \n**Enable Verify:** {verify_bool} \n**Enable Entry:** {entry_bool} \n**Enable Codeword:** {codeword_bool} \n**Enable Welcome:** {welcome_bool} \n**Enable Introduction:** {introduction_bool} \n**Enable Instruction:** {instructions_bool} \n**Enable Verification Log:** {verification_log_bool} \n**Enable Partner Verification Log:** {partner_verification_bool}"
        bool_embed = discord.Embed(title="**Overseer Settings**", description="# **Enabled / Disabled Settings**:\n" + bools, color=clr)
        bool_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        bool_embed.add_field(name="Date", value="{}".format(timestamp))
        bool_embed.set_footer(text="Page    2 / 5")
        all_embeds.append(bool_embed)
        
        # Moderation: All settings
        mods = f"# **Miscellaneous:**\n**Threshold Action**: {threshold_action} \n**Warn Threshold**: {warn_threshold} \n**Incident Threshold**: {incident_threshold} \n**Member Blacklist Auto Action:** {member_auto_action} \n\n# **Roles:** \n**Staff Role**: {staff_role} \n**Moderator Role**: {mod_role} \n**Admin Role**: {admin_role} \n**Quarantine Role**: {quarantine_role} \n**Booster Role**: {booster_role} \n**Server Partner**: {serverpartner_role} \n\n# **Channels:** \n**Public Moderation Channel**: {public_moderation_channel} \n**Log Channel**: {log_channel} \n**Mod Log Channel**: {modlog_channel} \n**Staff Channel**: {staff_channel} \n**Boost Channel**: {boost_channel} \n**Navigation Channel**: {map_channel} \n**Quarantine Channel**: {quarantine_channel}"
        mod_embed = discord.Embed(title="**Overseer Settings**", description="# **Moderation Settings**:\n" + mods, color=clr)
        mod_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        mod_embed.add_field(name="Date", value="{}".format(timestamp))
        mod_embed.set_footer(text="Page    3 / 5")
        all_embeds.append(mod_embed)
        
        
        # Verification: All settings
        verif = f"# **Roles**:\n**ID-Verified Role**: {id_role}\n**Newly Joined Member Role**: {freshjoin_role} \n**Unverified Role**: {unverified_role} \n**Member / Verified Role**: {member_role} \n**Crossverified Role**: {crossverified_role} \n\n# **Channels**: \n**Verification Log Channel**: {verification_log_channel} \n**Partner Verification Log Channel**: {partner_verification_channel} \n**Welcome Channel**: {welcome_channel}"
        ver_embed = discord.Embed(title="**Overseer Settings**", description="# **Verification Settings**:\n" + verif, color=clr)
        ver_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        ver_embed.add_field(name="Date", value="{}".format(timestamp))
        ver_embed.set_footer(text="Page    4 / 5")
        all_embeds.append(ver_embed)
        
        verif_2 = f"# **Miscellaneous:** \n**Entry Ticket Category:** {entry_category_channel} \n**Codeword**: {codeword} \n\n**Welcome Message**: {welcome_message} \n\n**Introduction Message**: {introduction} \n\n**Instruction Message**: {instruction}"
        ver2_embed = discord.Embed(title="**Overseer Settings**", description="# **Verification Settings**:\n" + verif_2, color=clr)
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



    # SERVER BLACKLISTS
    
    @server.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def adds(self, ctx, reason: str, *, server: str):
        """ Add servers to the blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' sub-command of 'overseer settings blacklist server' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).server_blacklist()
        
        is_in = False
        for items in b["log"]:
            if items["server"] == server:
                is_in = True
        
        if is_in == True:
            await ctx.send("This server is already blacklisted.")
            return
        
        b["log"].append({
                            "server" : server,
                            "reason" : reason
                        })
        
        await self.config.guild(guild).server_blacklist.set(b)

        # Print the message, if successful.
        await ctx.send(f"You have successfully added {server} to the server blacklist, {author.name}.")

    @server.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def deletes(self, ctx, *, server: str):
        """ Remove blacklisted servers. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "remove_blacklist", "Running 'remove_blacklist' sub-command of 'overseer settings blacklist server' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).server_blacklist()
        
        is_in = False
        for items in b["log"]:
            if items["server"].lower() == server.lower():
                is_in = True
                target = items
        
        if is_in == False:
            await ctx.send("This server is not blacklisted.")
            return
        
        b["log"].remove(target)
        
        await self.config.guild(guild).server_blacklist.set(b)

        # Print the message, if successful.
        await ctx.send(f"You have successfully removed {server} from the server blacklist, {author.name}.")
    
    @server.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def listshow(self, ctx):
        """ Show the server blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'list_show' sub-command of 'overseer settings blacklist server' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).server_blacklist()
        
        printmessage = "here is the blacklist: \n "
        blacklist = b["log"]
        
        if blacklist == []:
            printmessage += "The blacklist is currently empty."
            await ctx.send(printmessage)
        else:
            all_embeds = []
            pagination_items = 5
                
            total_items = len(blacklist)
                
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
                                                description=f"# ** Server Blacklist**\n", 
                                                color=clr)
                embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                offset = (page-1)*pagination_items
                if abs(page*pagination_items - total_items) < pagination_items:
                    if total_items <= pagination_items:
                        L = pagination_items-abs(page*pagination_items - total_items)
                    else:
                        L = pagination_items-abs(page*pagination_items - total_items) + 1
                    for individ in blacklist[offset:offset+L]:
                            server = individ["server"]
                            reason = individ["reason"]
                            embed.description += f"```Server:       {server}\nReason:       {reason}```\n"
                else:
                    for individ in blacklist[offset : offset+pagination_items]:
                            server = individ["server"]
                            reason = individ["reason"]
                            embed.description += f"```Server:       {server}\nReason:       {reason}```\n"
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

    @server.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def emptyout(self, ctx):
        """ Clear the server blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clear' sub-command of 'overseer settings blacklist server' command.")
            return
        
        # Set the blacklist.
        b = {"log" : []}
        await self.config.guild(guild).server_blacklist.set(b)

        # Print the message, if successful.
        await ctx.send(f"You have successfully cleared the server blacklist, {author.name}.")
    
    @server.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def changereason(self, ctx, reason: str, *, server: str):
        
        """ Change the reason of a server's blacklist entry. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'reason' sub-command of 'overseer settings blacklist server' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).server_blacklist()

        is_in = False
        for items in b["log"]:
            if items["server"] == server:
                is_in = True
                target = items
        
        if is_in == False:
            await ctx.send("This server is not blacklisted.")
            return
        
        b["log"].remove(target)
        target["reason"] = reason
        b["log"].append(target)
        
        await self.config.guild(guild).server_blacklist.set(b)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully changed the reason for the entry of {server} in the server blacklist, {author.name}.")
    
    @server.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def islisted(self, ctx, *, server: str):
        
        """ Find out if a server is blacklisted. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'is_listed' sub-command of 'overseer settings blacklist server' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).server_blacklist()

        is_in = False
        for items in b["log"]:
            if items["server"] == server:
                is_in = True
                target = items
        
        if is_in == False:
            await ctx.send("This server is not blacklisted.")
            return
        
        # Print the message, if successful.
        await ctx.send(f"The server {server} is blacklisted, {author.name}. \n Reason: {target['reason']}")
    
    
    
    # MEMBER BLACKLISTS

    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def addm(self, ctx, member: discord.User, *, reason: str=None):
        """ Add members to the blacklist with an optional reason. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' sub-command of 'overseer settings blacklist member' command.")
            return
        
        if reason == None:
            reason = "Reason not set."
        
        # Set the blacklist.
        b = await self.config.guild(guild).member_blacklist()
        
        is_in = False
        for items in b["log"]:
            if items["member_id"] == member.id:
                is_in = True
        
        if is_in == True:
            await ctx.send("This member is already blacklisted.")
            return
        
        b["log"].append({
                            "member_id" :   member.id, 
                            "member_name":  member.name,
                            "reason" : reason
                        })
        
        await self.config.guild(guild).member_blacklist.set(b)

        # Print the message, if successful.
        await ctx.send(f"You have successfully added {member.name} to the member blacklist, {author.name}.")

    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def mremove(self, ctx, member: str):
        """ Remove blacklisted members. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "remove_blacklist", "Running 'remove_blacklist' sub-command of 'overseer settings blacklist member' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).member_blacklist()

        is_in = False
        for items in b["log"]:
            if items["member_id"] == member.id:
                is_in = True
                target = items
        
        if is_in == False:
            await ctx.send("This member is not blacklisted.")
            return
        
        b["log"].remove(target)
        
        await self.config.guild(guild).member_blacklist.set(b)


        # Print the message, if successful.
        await ctx.send(f"You have successfully removed {member.name} from the member blacklist, {author.name}.")
    
    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def list_showm(self, ctx):
        """ Show the member blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'list_show' sub-command of 'overseer settings blacklist member' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).member_blacklist()
        blacklist = b["log"]
        printmessage = "Here is the blacklist: \n "
        
        if blacklist == []:
            printmessage += "The blacklist is currently empty."
            await ctx.send(printmessage)
        else:
            all_embeds = []
            pagination_items = 5
                
            total_items = len(blacklist)
                
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
                                                description=f"# ** Member Blacklist**\n", 
                                                color=clr)
                embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                offset = (page-1)*pagination_items
                if abs(page*pagination_items - total_items) < pagination_items:
                    if total_items <= pagination_items:
                        L = pagination_items-abs(page*pagination_items - total_items)
                    else:
                        L = pagination_items-abs(page*pagination_items - total_items) + 1
                    for individ in blacklist[offset:offset+L]:
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            content = individ["reason"]
                            embed.description += f"```Member:       {member_name} ({member_id})\nReason         {content}```\n"
                else:
                    for individ in blacklist[offset : offset+pagination_items]:
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            content = individ["reason"]
                            embed.description += f"```Member:       {member_name} ({member_id})\nReason         {content}```\n"
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

    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def emptym(self, ctx):
        """ Clear the member blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clear' sub-command of 'overseer settings blacklist member' command.")
            return
        b = {"log": []}
        # Set the blacklist.
        await self.config.guild(guild).member_blacklist.set(b)

        # Print the message, if successful.
        await ctx.send(f"You have successfully cleared the member blacklist, {author.name}.")

    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def reasonm(self, ctx, member:discord.User, *, reason: str):
        
        """ Change the reason of a user's blacklist entry. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'reason' sub-command of 'overseer settings blacklist member' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).member_blacklist()

        is_in = False
        for items in b["log"]:
            if items["member_id"] == member.id:
                is_in = True
                target = items
        
        if is_in == False:
            await ctx.send("This member is not blacklisted.")
            return
        
        b["log"].remove(target)
        target["reason"] = reason
        b["log"].append(target)
        
        await self.config.guild(guild).member_blacklist.set(b)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully changed the reason for the entry of {member.name} in the member blacklist, {author.name}.")
    
    @member.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def is_listedm(self, ctx, member: discord.User): 
        
        """ Find out if a member is blacklisted. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'is_listed' sub-command of 'overseer settings blacklist member' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).member_blacklist()

        is_in = False
        for items in b["log"]:
            if items["member_id"] == member.id:
                is_in = True
                target = items
        
        if is_in == False:
            await ctx.send("This member is not blacklisted.")
            return
        
        # Print the message, if successful.
        await ctx.send(f"The member {member.name} is blacklisted, {author.name}. \n Reason: {target['reason']}")
    

    
    # SERVER PARTNERS
    
    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def add(self, ctx, rep: discord.User, *, partner_server: str):
        
        """ Add partner server to the list with a representative. Manager will be whoever entered the command. You need to enter a server ID, then the user ID. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' subcommand of 'partners' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        partners = await self.config.guild(guild).server_partners()
        
        partners[partner_server.id] = {
            "server_name" : partner_server,
            "server_rep" : [rep.name, rep.id],
            "manager" : [author.name, author.id],
            "time" : ts,
            "verifiedrole" : ""
        }

        await self.config.guild(guild).server_partners.set(partners)
        
        # Log embed
        embed = discord.Embed(title="**Partner Servers**", description=f"A partner server has been added to the list.", color=clr)
        embed.add_field(name="Server Name", value=f"{partner_server.name}")
        embed.add_field(name="Server Rep", value=f"{rep.mention} ({rep.name} | ```{rep.id}```)", inline=False)    
        embed.add_field(name="Server Manager", value=f"{author.mention} ({author.name} | ```{author.id}```)", inline=False)    
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(ts))

    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def remove(self, ctx, *, partner_server: str):
        
        """ Remove a partner server from the list. You need to enter a discord server ID. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' subcommand of 'partners' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        partners = await self.config.guild(guild).server_partners()
        
        for keys in partners:
            if partners[keys]["server_name"].lower() == partner_server.lower():
                target = partners[keys]
        
        if target == None:
            await ctx.send(f"This server is currently not partnered with {partner_server}.")
            return
        
        partners.pop(partner_server)

        await self.config.guild(guild).server_partners.set(partners)
        await ctx.send(f"You have successfully removed the server {target['server_name']} from the list.")

    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def manager(self, ctx, manager: discord.User, *, partner_server: str):
        
        """ Change the manager of a partner server. You need to enter a server ID, then a user ID. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' subcommand of 'partners' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        partners = await self.config.guild(guild).server_partners()
        
        for keys in partners:
            if partners[keys]["server_name"].lower() == partner_server.lower():
                target = partners[keys]
        
        if target == None:
            await ctx.send(f"This server is currently not partnered with {partner_server}.")
            return
        target['manager'] = [manager.name, manager.id]
        await self.config.guild(guild).server_partners.set(partners)
        
        await ctx.send(f"You have successfully changed the manager of the partner server {partner_server} to the user {manager.name} (```{manager.id}```).")
    
    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def rep(self, ctx, rep: discord.User, *, partner_server: str):
        
        """ Change the representative of a partner server. You need to enter a server ID, then a user ID. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' subcommand of 'partners' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        partners = await self.config.guild(guild).server_partners()
        
        for keys in partners:
            if partners[keys]["server_name"].lower() == partner_server.lower():
                target = partners[keys]
        
        if target == None:
            await ctx.send(f"This server is currently not partnered with {partner_server}.")
            return
        target['server_rep'] = [rep.name, rep.id]
        await self.config.guild(guild).server_partners.set(partners)
        
        await ctx.send(f"You have successfully changed the representative of the partner server {partner_server} to the user {rep.name} (```{rep.id}```).")
    
    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def verificationrole(self, ctx, verification_role: str, *, partner_server: str):
        
        """ Change the verificationrole of a partner server. You need to enter a server ID, then a user ID. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' subcommand of 'partners' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        partners = await self.config.guild(guild).server_partners()
        
        for keys in partners:
            if partners[keys]["server_name"].lower() == partner_server.lower():
                target = partners[keys]
        
        if target == None:
            await ctx.send(f"This server is currently not partnered with {partner_server}.")
            return
        
        target['verifiedrole'] = verification_role
        await self.config.guild(guild).server_partners.set(partners)
        
        await ctx.send(f"You have successfully changed the verification role of the partner server {partner_server} to {verification_role}.")
    
    @app_commands.command(description="View all current server partnerships.")
    @app_commands.guild_only()
    async def server_partners(self, interaction: discord.Interaction):

        """ View the partner server list. """
        
        author = interaction.user
        guild = interaction.guild
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        clr = 0x4c001f

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'partners' command.")
            return
        
        partner = await self.config.guild(guild).server_partners()
        
        partners = list(partner.values())
        
        if partners:
            all_embeds = []
            pagination_items = 6
                
            total_items = len(partners)
                
            total_pages_items = total_items // pagination_items+1
            if total_items % pagination_items==0:
                total_pages_items = total_items // pagination_items
            else:
                total_pages_items = total_items // pagination_items+1
                
            for page in range(1, total_pages_items+1):
                    
                # Log embed
                embed = discord.Embed(title="", 
                                                description=f"# **Partner Servers**:", 
                                                color=clr)
                embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                offset = (page-1)*pagination_items
                if abs(page*pagination_items - total_items) < pagination_items:
                    for individ in partners[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                        server_name = individ["server_name"]
                        rep_name = individ["server_rep"][0]
                        rep_id = individ["server_rep"][1]
                        manager_name = individ["manager"][0]
                        manager_id = individ["manager"][1]
                        role = individ["verifiedrole"]
                        if role == "":
                            role = "Unknown."
                        date = individ["time"]
                        embed.description += f"Server: {server_name} \nRepresentative: {rep_name} ```{rep_id}```\nManager: {manager_name} ```{manager_id}```\nVerification Role: {role} \nDate of Establishment: {date}"
                else:
                    for individ in partners[offset : offset+pagination_items]:
                        server_name = individ["server_name"]
                        rep_name = individ["server_rep"][0]
                        rep_id = individ["server_rep"][1]
                        manager_name = individ["manager"][0]
                        manager_id = individ["manager"][1]
                        role = individ["verifiedrole"]
                        if role == "":
                            role = "Unknown."
                        date = individ["time"]
                        embed.description += f"Server: {server_name} \nRepresentative: {rep_name} ```{rep_id}```\nManager: {manager_name} ```{manager_id}```\nVerification Role: {role} \nDate of Establishment: {date}"
                embed.add_field(name="Date", value="{}".format(timestamp))
                embed.set_footer(text=f"Page {page} / {total_pages_items}")
                        
                all_embeds.append(embed)
            current_page = 0
            message = await interaction.send_message(embed=all_embeds[current_page])
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
                            if current_page <= 3:
                                await message.edit(embed=all_embeds[current_page])
                            elif current_page +1> 3:
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
        else:
            await interaction.send_message(f"You do not have any server partners.", ephemeral=True)
            return
        

    
    # Booster Role Automation
    
    @app_commands.command(description="Change or request a custom role for boosting.")
    @app_commands.guild_only()
    @app_commands.describe(custom_name="Enter a valid name for the role!", custom_color="Enter a valid hex code (format: #000000 as example).")
    async def boosting_role(self, interaction: discord.Interaction, custom_name: str, custom_color: str):

        """ Create or manage a boosting role. """
        
        member = interaction.user
        guild = interaction.guild
        clr = 0x990000
        boost_list = await self.config.guild(guild).boosting_users()
        boost_role = get(guild.roles,id= await self.config.guild(guild).booster_role())
        dummy = False
        
        if boost_role == None:
            return
        
        if len(custom_colour) > 7:
            await interaction.send_message(f"Please enter a valid hex colour code (format #000000).", ephemeral=True)
            return
        else:
            if custom_colour[0] == "#":
                custom_colour = custom_colour[0:]
                
        
        if boost_role in member.roles:
            
            if boost_list != {}:
                for keys in boost_list:
                    if boost_list[keys]["user_id"] == member.id:
                        dummy = True
                        memberlog = boost_list[keys]
            colour = f"0x{custom_colour}"
            crole = await guild.create_role(name=custom_name, colour=discord.Colour(colour))
            
            if dummy == False:
                boost_list[member.id] = {
                    "user_id" : member.id,
                    "user_name" : member.name,
                    "date" : timestamp,
                    "custom_role" : crole.id,
                    "custom_colour" : f"0x{custom_colour}",
                    "custom_name" : custom_name
                }
            else:
                memberlog["custom_role"] = crole.id
                memberlog["custom_colour"] = f"0x{custom_colour}"
                memberlog["custom_name"] = custom_name
                
        else:
            await interaction.send_message(f"You have not boosted the server yet. Boost the server to request a (or change your) custom role.", ephemeral=True)
            return
        
        

    
    
    
    # 
    
    
    

    
    # LOGS: MODERATION GENERAL
        
    @moderation.group(name="logging")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def logging(self, ctx):
        """ Anything regarding logging on moderation. """

    @logging.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def clearlogs(self, ctx, choice: str=None):
        """ Clear the logs (for moderation.) Leaving it empty will delete all. Options: Kicks, bans, incidents, timeouts, warns, quarantines, notes. """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clear' sub-command of 'moderation logging' command.")
            return

        if choice == None:
            await ctx.send("Are you sure that you want to purge all logs?")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond.")
                return
            if msg.content!=None:
                if "yes" in msg.content:
                    await self.config.guild(guild).ban_logs.set({})
                    await self.config.guild(guild).incident_logs.set({"logs" : []})
                    await self.config.guild(guild).kick_logs.set({"logs" : []})
                    await self.config.guild(guild).timeout_logs.set({"logs" : []})
                    await self.config.guild(guild).warn_logs.set({"logs" :[]})
                    await self.config.guild(guild).quarantine_logs.set({})
                    await self.config.guild(guild).notes.set({})

                    settings = f"\n **Log Purge:** \n All moderation logs have been purged."
                
                    embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    embed.set_footer(text="Date - {}".format(timestamp))
                    await ctx.send(embed=embed)
                elif "no" in msg.content:
                    await ctx.send("I have not deleted the logs, the command has failed.")
                    return
            else:
                await ctx.send("My apologies, however, I have encountered an error. Please try again.")
                return
        elif choice.lower() in ["kicks"]:
            await self.config.guild(guild).kick_logs.set({"logs" : []})

            settings = f"\n **Log Purge:** \n The kick logs have been purged."
                
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["bans"]:
            await self.config.guild(guild).ban_logs.set({})

            settings = f"\n **Log Purge:** \n The ban logs have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["incidents"]:
            await self.config.guild(guild).incident_logs.set({"logs" : []})

            settings = f"\n **Log Purge:** \n The incident logs have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["timeouts"]:
            await self.config.guild(guild).timeout_logs.set({"logs" : []})

            settings = f"\n **Log Purge:** \n The timeout logs have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["warns"]:
            await self.config.guild(guild).warn_logs.set({"logs" : []})

            settings = f"\n **Log Purge:** \n The warn logs have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["quarantines"]:
            await self.config.guild(guild).quarantine_logs.set({})

            settings = f"\n **Log Purge:** \n The quarantine logs have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["notes"]:
            await self.config.guild(guild).notes.set({})

            settings = f"\n **Log Purge:** \n The note logs have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        else:
            await ctx.send("My apologies, you have entered the wrong option.")
            return
    
    @logging.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def delete(self, ctx, choice: str, number: int):
        """ Delete a specific log (for moderation.) \nOptions: Kicks, bans, incidents, timeouts, warns, quarantines."""

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target_log = None
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'delete' sub-command of 'moderation logging' command.")
            return

        if choice not in ["kicks", "bans", "ban", "kick", "quarantines", "quarantine", "timeouts", "timeout", "warns", "warn"]:
            await ctx.send("My apologies, however, you need to enter a valid log category.")
            return
        elif choice.lower() in ["kicks"]:
            kick_logs = await self.config.guild(guild).kick_logs()
            
            for items in kick_logs["logs"]:
                if items["number"] == number:
                    target_log = items
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the respective log category.")
                return
            
            kick_logs["logs"].remove(target_log)
            await self.config.guild(guild).kick_logs.set(kick_logs)
            settings = f"\n **Log Delete:** \n The kick log #{number} has been deleted."
                
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            await ctx.send(embed=embed)
        elif choice.lower() in ["bans"]:
            ban_logs = await self.config.guild(guild).ban_logs()
            
            for keys in ban_logs:
                if ban_logs[keys]["number"] == number:
                    target_log = ban_logs[keys]
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the respective log category.")
                return
            
            ban_logs.pop(target_log)
            await self.config.guild(guild).ban_logs.set(ban_logs)

            settings = f"\n **Log Delete:** \n The ban log #{number} has been deleted."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["incidents"]:
            incident_logs = await self.config.guild(guild).incident_logs()
            
            for items in incident_logs["logs"]:
                if items["number"] == number:
                    target_log = items
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the respective log category.")
                return
            
            incident_logs["logs"].remove(target_log)
            await self.config.guild(guild).incident_logs.set(incident_logs)
            settings = f"\n **Log Delete:** \n The incident log #{number} has been deleted."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["timeouts"]:
            timeout_logs = await self.config.guild(guild).timeout_logs()
            
            for items in timeout_logs["logs"]:
                if items["number"] == number:
                    target_log = items
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the respective log category.")
                return
            
            timeout_logs["logs"].remove(target_log)
            await self.config.guild(guild).timeout_logs.set(timeout_logs)
            settings = f"\n **Log Delete:** \n The timeout log #{number} has been deleted."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["warns"]:
            warn_logs = await self.config.guild(guild).warn_logs()
            
            for items in warn_logs["logs"]:
                if items["number_warn"] == number:
                    target_log = items
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the respective log category.")
                return
            
            warn_logs["logs"].remove(target_log)
            await self.config.guild(guild).warn_logs.set(warn_logs)
            settings = f"\n **Log Delete:** \n The warn log #{number} has been deleted."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["quarantines"]:
            quarantine_logs = await self.config.guild(guild).quarantine_logs()
            
            for keys in quarantine_logs:
                if quarantine_logs[keys]["number"] == number:
                    target_log = quarantine_logs[keys]
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the respective log category.")
                return
            
            quarantine_logs.pop(target_log)
            await self.config.guild(guild).quarantine_logs.set(quarantine_logs)

            settings = f"\n **Log Delete:** \n The quarantine log #{number} has been deleted."
            
            embed = discord.Embed(title="Overseer Moderation: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        else:
            await ctx.send("My apologies, you have entered the wrong option.")
            return
    
    @logging.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def view_logs(self, ctx, choice: str):
        
        """ View a certain log."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())

        
        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'view_logs' sub command of 'moderation logging'.")
            return

        
        if choice.lower() not in ["kicks", "bans", "warns", "quarantines", "timeouts", "incidents"]:
            await ctx.send(f"My apologies, dear {author.name}, however, I can only accept the names of existing log categories. \nExisting categories are: \n- kicks, \n- bans, \n- warns,\n- timeouts, \n- quarantines")
            return
        elif choice.lower() == "warns":
            warn_log = await self.config.guild(guild).warn_logs()
            warn_logs = warn_log["logs"]
            if warn_logs:
                all_embeds = []
                pagination_items = 5
                
                total_items = len(warn_logs)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Warns**\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in warn_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            number = individ["number_warn"]
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in warn_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            number = individ["number_warn"]
                            staff_name = individ["staff_name"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if there are no warns presently.')
        elif choice.lower() == "timeouts":
            timeout_log = await self.config.guild(guild).timeout_logs()
            timeout_logs = timeout_log["logs"]
            if timeout_logs:
                all_embeds = []
                pagination_items = 6
                
                total_items = len(timeout_logs)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Timeouts**\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in timeout_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            duration = individ["duration"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nDuration:        {duration} second(s)\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in timeout_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            duration = individ["duration"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nDuration:        {duration} second(s)\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if there are no timeouts presently.')
        elif choice.lower() == "kicks":
            kick_log = await self.config.guild(guild).kick_logs()
            kick_logs = kick_log["logs"]
            if kick_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(kick_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Kicks**\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in kick_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in kick_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if there are no kicks presently.')
        elif choice.lower() == "bans":
            ban_log = await self.config.guild(guild).ban_logs()
            ban_logs = list(ban_log.values())
            if ban_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(ban_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Bans**\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in ban_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in ban_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if there are no bans presently.')
        elif choice.lower() == "quarantines":
            quarantine_log = await self.config.guild(guild).quarantine_logs()
            quarantine_logs = list(quarantine_log.values())
            if quarantine_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(quarantine_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Quarantines**", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in quarantine_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            rls = ""
                            for roles in individ["roles"]:
                                item = get(guild.roles, id=roles)
                                rls+=f"{item.mention} "
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}\nRoles:            {rls}```"
                    else:
                        for individ in quarantine_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            for roles in individ["roles"]:
                                item = get(guild.roles, id=roles)
                                rls+=f"{item.mention} "
                            number = individ["number"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Number:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}\nRoles:            {rls}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if there are no quarantines presently.')
        elif choice.lower() == "incidents":
            incident_log = await self.config.guild(guild).incident_logs()
            incident_logs = incident_log["logs"]
            if incident_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(incident_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Incidents**\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in incident_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            type_inc = individ["incident_type"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            try:
                                number = individ["number"]
                            except:
                                number = individ["number_warn"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Type:            {type_inc}\nNumber:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in incident_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            type_inc = individ["incident_type"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            try:
                                number = individ["number"]
                            except:
                                number = individ["number_warn"]
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            embed.description += f"```Type:            {type_inc}\nNumber:          {number}\nUser:            {member_name} ({member_id})\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if there are no incidents presently.')
    
    
    # LOGS: MODERATION USERS
    
    @logging.group(name="users")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def users(self, ctx):
        """ Anything regarding logging (on moderation of users). """
        
    @users.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def purge(self, ctx, user: discord.User, choice: str=None):
        """ Purge a user's logs. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'purge' sub-command of 'moderation logging users' command.")
            return
        
        # Get user, make sure there is existing log
        userlog = await self.config.guild(guild).users()
        for keys in userlog:
            if userlog[keys]["member_id"] == user.id:
                target = userlog[keys]
            
        if target == None:
            await ctx.send("This user does not have any logs.")
            return
        
        if choice == None:
            await ctx.send("Are you sure that you want to purge all logs of this user?")
            try:
                async with asyncio.timeout(300):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send(f"You have taken too long to respond.")
                return
            if msg.content!=None:
                if "yes" in msg.content:
                    
                    target["bans"] = []
                    target["warns"] = []
                    target["kicks"] = []
                    target["timeouts"] = []
                    target["quarantines"] = []
                    target["incidents"] = []
                    target["threshold"] = 0

                    settings = f"\n **Log Purge:** \n All moderation logs of {user.name} have been purged."
                
                    embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    embed.set_footer(text="Date - {}".format(timestamp))
                    await ctx.send(embed=embed)
                elif "no" in msg.content:
                    await ctx.send(f"I have not deleted the logs of {user.name}, the command has failed.")
                    return
            else:
                await ctx.send("My apologies, however, I have encountered an error. Please try again.")
                return
        elif choice.lower() in ["kicks"]:
            target["kicks"] = []

            settings = f"\n **Log Purge:** \n The kick logs of {user.name} have been purged."
                
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["bans"]:
            target["bans"] = []

            settings = f"\n **Log Purge:** \n The ban logs of {user.name} have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["incidents"]:
            target["incidents"] = []

            settings = f"\n **Log Purge:** \n The incident logs of {user.name} have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["timeouts"]:
            target["timeouts"] = []

            settings = f"\n **Log Purge:** \n The timeout logs of {user.name} have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["warns"]:
            target["warns"] = []

            settings = f"\n **Log Purge:** \n The warn logs of {user.name} have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["quarantines"]:
            target["quarantines"] = []

            settings = f"\n **Log Purge:** \n The quarantine logs of {user.name} have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["notes"]:
            target["notes"] = []

            settings = f"\n **Log Purge:** \n The notes of {user.name} have been purged."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User's Notes", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        else:
            await ctx.send("My apologies, you have entered the wrong option.")
            return

        userlog[user.id] = target
        await self.config.guild(guild).users.set(userlog)
    
    @users.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def _del(self, ctx, user: discord.User, choice: str, number: int):
        """ Delete a single of a user's logs with a number. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        target_log = None
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'delete' sub-command of 'moderation logging users' command.")
            return
        
        # Get user, make sure there is existing log
        userlog = await self.config.guild(guild).users()
        for keys in userlog:
            if userlog[keys]["member_id"] == user.id:
                target = userlog[keys]
        
        if target == None:
            await ctx.send("This user does not have any logs.")
            return
        
        if number <=0:
            await ctx.send("My apologies, however, you need to enter a valid non-zero positive number.")
            return
        
        if choice.lower() not in ["kicks", "bans", "ban", "kick", "quarantines", "quarantine", "timeouts", "timeout", "warns", "warn"]:
            await ctx.send("My apologies, however, you need to enter either kicks, bans, quarantines, timeouts, or warns.")
            return
        elif choice.lower() in ["kicks", "kick"]:

            for items in target["kicks"]:
                if items["member_id"] == user.id and items["number"]== number:
                    target_log = items
            target["kicks"].remove(target_log)
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the log.")
                return
        
            settings = f"\n **Log Delete:** \n The kick log #{number} has been purged from {user.name}'s kick logs."
                
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["bans", "ban"]:

            for items in target["bans"]:
                if items["member_id"] == user.id and items["number"]== number:
                    target_log = items
            target["bans"].remove(target_log)
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the log.")
                return
        
            settings = f"\n **Log Delete:** \n The ban log #{number} has been purged from {user.name}'s ban logs."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["incidents", "incident"]:
            for items in target["incidents"]:
                if items["member_id"] == user.id and items["number"]== number:
                    target_log = items
            target["incidents"].remove(target_log)
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the log.")
                return
        
            settings = f"\n **Log Delete:** \n The incident log #{number} has been deleted from {user.name}'s incident logs."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["timeouts", "timeout"]:

            for items in target["timeouts"]:
                if items["member_id"] == user.id and items["number"]== number:
                    target_log = items
            target["timeouts"].remove(target_log)
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the log.")
                return
        
            settings = f"\n **Log Delete:** \n The timeout log #{number} has been purged from {user.name}'s timeout logs."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["warns", "warn"]:
            for items in target["warns"]:
                if items["member_id"] == user.id and items["number_warn"]== number:
                    target_log = items
            target["warns"].remove(target_log)
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the log.")
                return
        
            settings = f"\n **Log Delete:** \n The warn log #{number} has been purged from {user.name}'s warn logs."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["quarantines", "quarantine"]:
            
            for items in target["quarantines"]:
                if items["member_id"] == user.id and items["number"]== number:
                    target_log = items
            target["quarantines"].remove(target_log)
            
            if target_log == None:
                await ctx.send("My apologies, however, I could not find this entry in the log.")
                return
        
            settings = f"\n **Log Delete:** \n The quarantine log #{number} has been purged from {user.name}'s quarantine logs."
            
            embed = discord.Embed(title="Overseer Moderation: Update to User Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        else:
            await ctx.send("My apologies, you have entered the wrong option.")
            return

        userlog[user.id] = target
        await self.config.guild(guild).users.set(userlog)
    
    @users.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def sync_init(self, ctx):
        """ Synchronise all member logs. \n This means to initialise a user log for every server member, if there is none. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        user_logs = await self.config.guild(guild).users()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'sync_init' subcommand of 'moderation logging users' command.")
            return
        
        tally = 0
        
        for member in guild.members:
            target = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target = user_logs[keys]

            if target == None:
                tally += 1
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
        await ctx.send(f"Dear {author.name}, I have synchronised the user logs, and added {tally} users.")
        await self.config.guild(guild).users.set(user_logs)
    
    @users.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def view(self, ctx, member: discord.User, choice: str):
        
        """ View a certain log of a user. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())

        
        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'view' sub command of 'moderation logging users'.")
            return
        
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
                "bans" : {}, # Ban logs
                "quarantines" : {}, # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]
        
        
        if choice.lower() not in ["kicks", "bans", "warns", "quarantines", "timeouts", "threshold"]:
            await ctx.send(f"My apologies, dear {author.name}, however, I can only accept the names of existing log categories. \nExisting categories are: \n- kicks, \n- bans, \n- warns,\n- timeouts, \n- quarantines")
            return
        elif choice.lower() == "warns":
            warn_logs = target["warns"]
            if warn_logs:
                all_embeds = []
                pagination_items = 1
                
                total_items = len(warn_logs)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Warns**\n\n**User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in warn_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            number = individ["number_warn"]
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in warn_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            number = individ["number_warn"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if {member.mention} has no warns presently.')
        elif choice.lower() == "timeouts":
            timeout_logs = target["timeouts"]
            if timeout_logs:
                all_embeds = []
                pagination_items = 6
                
                total_items = len(timeout_logs)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Timeouts**\n\n**User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in timeout_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            duration = individ["duration"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nDuration:        {duration} second(s)\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in timeout_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            duration = individ["duration"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nDuration:        {duration} second(s)\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if {member.mention} has no timeouts presently.')
        elif choice.lower() == "kicks":
            kick_logs = target["kicks"]
            if kick_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(kick_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Kicks**\n\n**User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in kick_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in kick_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if {member.mention} has no kicks presently.')
        elif choice.lower() == "bans":
            ban_logs = target["bans"]
            if ban_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(ban_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Bans**\n\n**User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in ban_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in ban_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if {member.mention} has no bans presently.')
        elif choice.lower() == "quarantines":
            quarantine_logs = target["quarantines"]
            if quarantine_logs:
                all_embeds = []
                
                pagination_items = 6

                total_items = len(quarantine_logs)
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Moderation Log: Quarantines**\n\n**User:** {member.name} ({member.id})\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in quarantine_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            rls = ""
                            for roles in individ["roles"]:
                                item = get(guild.roles, id=roles)
                                rls+=f"{item.mention} "
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}\nRoles:            {rls}```"
                    else:
                        for individ in quarantine_logs[offset : offset+pagination_items]:
                            reason = individ["reason"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            for roles in individ["roles"]:
                                item = get(guild.roles, id=roles)
                                rls+=f"{item.mention} "
                            number = individ["number"]
                            embed.description += f"```Number:          {number}\nReason:          {reason}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}\nRoles:            {rls}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if {member.mention} has no quarantines presently.')
        elif choice.lower() == "threshold":
            await ctx.send(f"The threshold count of {member.name} is currently at: {target['threshold']}.")

    
    # LOGS: VERIFICATION
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def show(self, ctx, member: discord.User=None):
        
        """ List all the currently verified users in detail, or a single user. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())

        
        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        elif staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'view' sub command of 'moderation logging users'.")
            return
        
        verifications = await self.config.guild(guild).verified_users()
        
        if verifications == {}:
            await ctx.send("My apologies, however, there are no currently verified users.")
            return
        
        if member != None:
            target = None
            for keys in verifications:
                if verifications[keys]["member_id"] == member.id:
                    target = verifications[keys]
            
            if target == None:
                if member not in guild.members:
                    await ctx.send("This member is not verified, and not part of the server.")
                    return
                else:
                    await ctx.send("This member is not verified.")
                    return
            
            comment = target["comment"]
            staff_name = target["staff_name"]
            staff_id = target["staff_id"]
            log_url = target["log_url"]
            verification_method = target["verification_method"]
            log_id = target["log_id"]
            date = target["timestamp"]
            
            # Log embed
            embed = discord.Embed(
                title="", 
                description=f"** Verification **\n\n **User:** {member.name} ({member.id})\n\n", 
                color=clr)
            embed.add_field(name="Verification Method", value="{}".format(verification_method))
            embed.add_field(name="Verified by Staff", value="{} ({})".format(staff_name, staff_id))
            embed.add_field(name="Comment", value="```{}```".format(comment), inline=False)
            embed.add_field(name="Message URL", value="{}".format(log_url))
            embed.set_footer(text="Date: {}".format(date))
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            
            def check(reaction, user):
                        return (
                            user == author
                            and reaction.message.id == message.id
                            and str(reaction.emoji) in {"✅", "❌"}
                        )

            while True:
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0, check=check)
                        except TimeoutError:
                            break
                        else:
                            if str(reaction.emoji) == "✅":
                                # Close the embed
                                await message.delete()
                                return
                            elif str(reaction.emoji) == "❌":
                                # Delete the warning if the user is a moderator
                                if staffrole in author.roles:
                                    verifications.pop(str(member.id))
                                    await self.config.guild(ctx.guild).verified_users.set(verifications)
                                    await asyncio.sleep(5)
                                    await ctx.send("You have successfully deleted this verification.")
                                    await message.delete()
                                    break
                                else:
                                    await ctx.send("You do not have permission to delete warnings.")
                            await message.remove_reaction(reaction, user)

        else:
            member_vers = list(verifications.values())
            if member_vers != {}:
                all_embeds = []
                pagination_items = 6
                
                total_items = len(member_vers)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(
                                        title="**Verifications**", 
                                        description=f"The following users are verified in {guild.name}:", 
                                        color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    embed.description += f"\n───────────────────────"
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in member_vers[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            verification_method = individ["verification_method"]
                            birth_date = individ["birth_date"]
                            link = individ["log_url"]
                            date = individ["timestamp"]
                            embed.description += f"\nMember Name:          {member_name}\nBirth Date:          {birth_date}\nVerification Method:         {verification_method}\nLog URL:         {link}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}\nMember ID: ```{member_id}```"
                            embed.description += f"\n───────────────────────"
                    else:
                        for individ in member_vers[offset : offset+pagination_items]:
                            member_name = individ["member_name"]
                            member_id = individ["member_id"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            verification_method = individ["verification_method"]
                            birth_date = individ["birth_date"]
                            link = individ["log_url"]
                            date = individ["timestamp"]
                            embed.description += f"\nMember Name:          {member_name}\nBirth Date:          {birth_date}\nVerification Method:         {verification_method}\nLog URL:         {link}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}\nMember ID: ```{member_id}```"
                            embed.description += f"\n───────────────────────"
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f"My apologies, there are no verified members yet.")
                return
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def isverified(self, ctx, member: discord.User=None):
        
        """ Check whether or not a user is verified. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        verifications = await self.config.guild(guild).verified_users()
        
        target = None
        
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'isverified' command.")
            return
        
        
        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        elif staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        elif verifications == {}:
            await ctx.send("My apologies, however, there are no currently verified users.")
            return
        
    
        
        for keys in verifications:
            if verifications[keys]["member_id"] == member.id:
                target = verifications[keys]
                
        if target == None:
            if member not in guild.members:
                await ctx.send("This member is not verified, and not part of the server.")
                return
            else:
                await ctx.send("This member is not verified.")
                return
                
        comment = target["comment"]
        staff_name = target["staff_name"]
        staff_id = target["staff_id"]
        log_url = target["log_url"]
        verification_method = target["verification_method"]
        log_id = target["log_id"]
        date = target["timestamp"]
                
        # Log embed
        embed = discord.Embed(
            title="", 
            description=f"** Verification **\n\n **User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
            color=clr)
        embed.add_field(name="Verification Method", value="{}".format(verification_method))
        embed.add_field(name="Verified by Staff", value="{} (```{}```)".format(staff_name, staff_id))
        embed.add_field(name="Comment", value="```{}```".format(comment), inline=False)
        embed.add_field(name="Message URL", value="{} (``````)".format(log_url, log_id))
        embed.set_footer(text="Date: {}".format(date))
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                
        await ctx.send(embed=embed)
    
    @verification.group(name="log")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def log(self, ctx):
        """ Purge / backup the verification log / crossverification log. """
        
    @log.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def delete(self, ctx, choice: str=None):
        """ Purge the logs (for cross- or verification). Leaving it empty will delete both. """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'purge' sub-command of 'verification logs' command.")
            return

        if choice == None:
            await self.config.guild(guild).verified_users.set({})
            await self.config.guild(guild).crossverified_users.set({})
            settings = f"\n **Log Purge:** \n The verification and crossverification logs have been purged."
        
            embed = discord.Embed(title="Overseer Verification: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["verified", "verification", "verifications", "verified users", "verification logs"]:
            await self.config.guild(guild).verified_users.set({})
            settings = f"\n **Log Purge:** \n The verification logs have been purged."
        
            embed = discord.Embed(title="Overseer Verification: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["crossverified", "crossverification", "crossverifications", "crossverified users", "crossverification logs"]:
            await self.config.guild(guild).control_links.set({})
            settings = f"\n **Log Purge:** \n The crossverification logs have been purged."
        
            embed = discord.Embed(title="Overseer Verification: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        else:
            await ctx.send("My apologies, you have entered the wrong option. Please either leave it empty, choose 'verification', or 'crossverification'.")
        
    
    
    # LOGS: NOTES
    
    @commands.group(name="notes")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def notes(self, ctx):
        """ Anything regarding notes (of users). """
    
    @notes.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def addnote(self, ctx, member: discord.User, *, message: str):
        """ Add a note to a user. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        is_staff = False
        target = None
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'addnote' subcommand of 'notes' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        notes = await self.config.guild(guild).notes()
        user_logs = await self.config.guild(guild).users()
        
        for keys in notes:
            if notes[keys]["member_id"] == member.id:
                target_log = notes[keys]

        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
        
        if target_log == None:
            notes[member.id] = {
                "member_id" : member.id,
                "member_name" : member.name,
                "guild" : [guild.name, guild.id],
                "notes" : [], # User notes
            }
            target_log = notes[member.id]
        
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
        
        number = len(target["notes"])+1
        
        note = {
            "number" : number,
            "content" : message,
            "staff_name" : author.name,
            "staff_id" : author.id,
            "date" : timestamp
        }
        
        target["notes"].append(note)
        target_log["notes"].append(note)
        notes[member.id] = target_log
        user_logs[member.id] = target

        # Log embed
        embed = discord.Embed(title="**Notes**", description=f"**Notes**\n A note has been added to {member.name}.", color=clr)
        embed.add_field(name="**Number:**", value=number)
        if member not in guild.members:
            embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
        else:
            embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
        embed.add_field(name="**Content:**", value=f"{message}")
        embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)    
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        
        await self.config.guild(guild).notes.set(notes)
        await self.config.guild(guild).users.set(user_logs)
    
    @notes.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def clear(self, ctx, member: discord.User):
        """ Remove all notes from a user. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        target_log = None
        
        note_log = None
        user_note_log = None
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'addnote' subcommand of 'notes' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        notes = await self.config.guild(guild).notes()
        user_logs = await self.config.guild(guild).users()
        
        for keys in notes:
            if notes[keys]["member_id"] == member.id:
                target_log = notes[keys]

        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
        
        if target_log == None:
            await ctx.send(f"My apologies, {author.name}, however, I cannot delete a log that does not exist.")
            return
        
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
            await ctx.send(f"My apologies, {author.name}, however, I cannot delete a log that does not exist.")
            user_logs[member.id] = target
            await self.config.guild(guild).users.set(user_logs)
            return
        
        
        notes[member.id] = []
        user_logs[member.id] = []

        # Log embed
        embed = discord.Embed(title="**Notes**", description=f"**Notes**\n All notes have been deleted from {member.name}.", color=clr)
        if member not in guild.members:
            embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
        else:
            embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
        embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)    
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        
        await self.config.guild(guild).notes.set(notes)
        await self.config.guild(guild).users.set(user_logs)
      
    @notes.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def remove(self, ctx, member: discord.User, number: int):
        """ Remove a note from a user with a specific number. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        target_log = None
        
        note_log = None
        user_note_log = None
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'addnote' subcommand of 'notes' command.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        notes = await self.config.guild(guild).notes()
        user_logs = await self.config.guild(guild).users()
        
        for keys in notes:
            if notes[keys]["member_id"] == member.id:
                target_log = notes[keys]

        for keys in user_logs:
            if user_logs[keys]["member_id"] == member.id:
                target = user_logs[keys]
        
        if target_log == None:
            await ctx.send(f"My apologies, {author.name}, however, I cannot delete a log that does not exist.")
            return
        
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
            await ctx.send(f"My apologies, {author.name}, however, I cannot delete a log that does not exist.")
            user_logs[member.id] = target
            await self.config.guild(guild).users.set(user_logs)
            return
        
        
        for note in target["notes"]:
            if note["number"] == number:
                user_note_log = note
        for items in target_log:
            if items["number"] == number:
                note_log = items
                
        
        
        if user_note_log == None or note_log == None:
            await ctx.send(f"My apologies, {author.name}, however, I cannot delete a log that does not exist.")
            return
        target["notes"].remove(user_note_log)
        target_log["notes"].remove(note_log)
        notes[member.id] = target_log
        user_logs[member.id] = target

        # Log embed
        embed = discord.Embed(title="**Notes**", description=f"**Notes**\n A note has been deleted from {member.name}.", color=clr)
        embed.add_field(name="**Number:**", value=number)
        if member not in guild.members:
            embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
        else:
            embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
        embed.add_field(name="**Content:**", value=f"{note_log['message']}")
        embed.add_field(name="**by Staff**", value=f"{author.mention} ({author.name} | {author.id})", inline=False)    
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        
        await self.config.guild(guild).notes.set(notes)
        await self.config.guild(guild).users.set(user_logs)
        
    @notes.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def noteview(self, ctx, member: discord.User, choice: int=None):
        
        """ View a certain note of a user, or all of them of a user. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())

        
        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'view' sub command of 'moderation logging users'.")
            return
        
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
                "bans" : {}, # Ban logs
                "quarantines" : {}, # Quarantine logs
                "timeouts" : [], # Timeout logs
                "warns" : [], # Warn logs
                "notes" : [], # User notes
                "threshold" : 0 # incident count
            }
            target = user_logs[member.id]
        
        
        if choice == None: 
            note_logs = target["notes"]
            if note_logs:
                all_embeds = []
                pagination_items = 1
                
                total_items = len(note_logs)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Notes**\n\n**User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in note_logs[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            content = individ["content"]
                            number = individ["number"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            embed.description += f"```Number:          {number}\nContent:          {content}\n\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    else:
                        for individ in note_logs[offset : offset+pagination_items]:
                            content = individ["content"]
                            number = individ["number"]
                            staff_name = individ["staff_name"]
                            staff_id = individ["staff_id"]
                            date = individ["date"]
                            embed.description += f"```Number:          {number}\nContent:          {content}\n\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                    embed.description+="\n\nThe Date format is DD/MM/YYYY."
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
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page < total_pages_items - 3:
                                    current_page += 3
                                    await message.edit(embed=all_embeds[current_page])
                                elif total_pages_items -3<=current_page < total_pages_items:
                                    current_page += 3 - total_pages_items
                                    await message.edit(embed=all_embeds[current_page])
                            elif str(reaction.emoji) == "⏪":
                                if current_page <= 3:
                                    await message.edit(embed=all_embeds[current_page])
                                elif current_page +1> 3:
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
            else:
                await ctx.send(f'It seems as if {member.mention} has no notes presently.')
        elif choice != None:
            
            if choice <=0:
                await ctx.send(f"My apologies, however, you need to enter a valid note number.")
                return
            
            target_note = None
            
            note_logs = target["notes"]
            if note_logs:
                
                for items in note_logs:
                    if items["number"] == choice:
                        individ = items
                if target_note == None:
                    await ctx.send(f"My apologies, however, I could not find a note with this number.")
                    return
                
                # Log embed
                embed = discord.Embed(title="", 
                                                description=f"# ** Notes **\n\n**User:** {member.name} ({member.id})\n The Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                content = individ["content"]
                staff_name = individ["staff_name"]
                staff_id = individ["staff_id"]
                date = individ["date"]
                embed.description += f"```Number:          {choice}\nContent:          {content}\nby Staff:        {staff_name} ({staff_id})\nDate:            {date}```"
                embed.set_footer(text=f"Date: {timestamp}")
                         
                await ctx.send(embed=embed)
            else:
                await ctx.send(f'It seems as if {member.mention} has no notes presently.')

    
    
    # VERIFICATION COMMANDS
    
    @app_commands.command(description="Verify a user.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="Choose a member to verify.", crossverified="Optional. Enter the name of the server they are crossverifying from, otherwise, leave it empty.", birth_date="Enter the birthdate of the user in 'MONTH DD YYYY'.", comment="Optional comment.")
    async def verify(self, interaction: discord.Interaction, member: discord.Member, birth_date: str=None, crossverified: str=None, comment: str=None):
        
        """ Verify a member. """
        
        # Basic I/O.
        guild = interaction.guild
        author = interaction.user
        clr = 0x7c1734
        
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        memberrole = get(guild.roles, id = await self.config.guild(guild).member_role())
        unverifiedrole = get(guild.roles, id = await self.config.guild(guild).unverified_role())
        crossverifiedrole = get(guild.roles, id = await self.config.guild(guild).crossverified_role())
        id_role = get(guild.roles, id = await self.config.guild(guild).verification_role())
        
        modlog = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        verificationlog = get(guild.channels, id = await self.config.guild(guild).verification_log_channel())
        welcome = get(guild.channels, id = await self.config.guild(guild).welcome_channel())
        dob = get(guild.channels, id= await self.config.guild(guild).partner_verification_channel())
        log = get(guild.channels, id = await self.config.guild(guild).log_channel())
        
        
        welcome_message = await self.config.guild(guild).welcome_message()
        
        verifications = await self.config.guild(guild).verified_users()
        crossverifications = await self.config.guild(guild).crossverified_users()
        
        if not await self.config.guild(guild).enable_verification():
            await interaction.response.send_message("My apologies, however, this feature is disabled. You are required to enable it, before commencing.", ephemeral=True)
            return
        elif staffrole == None or memberrole == None or unverifiedrole == None or crossverifiedrole == None or modlog == None or log == None:
            await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the proper channels and roles.", ephemeral=True)
            return
        elif author==member:
            await interaction.response.send_message("My apologies, but, you cannot verify yourself.", ephemeral=True)
            return

        if await self.config.guild(guild).enable_verification_log():
            if verificationlog==None:
                await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the verification log channel, or disable the feature.", ephemeral=True)
                return
        elif await self.config.guild(guild).enable_welcome():
            if welcome == None:
                await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the welcome channel, or disable the feature.", ephemeral=True)
                return
        elif await self.config.guild(guild).enable_partner_verification():
            if dob == None:
                await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the partner verification log channel, or disable the feature.", ephemeral=True)
                return
        elif await self.config.guild(guild).enable_member_equal_id():
            if id_role == None:
                await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the ID-verified role, or disable the feature.", ephemeral=True)
                return
                
        
        is_verified = False
        
        if verifications != {}:
            for keys in verifications:
                if verifications[keys]["member_id"]==member.id:
                    is_verified = True
                    memberdict=verifications[keys]
        else:
            memberdict = None
        
        if birth_date == None:
            birth_date = "Not set."
        
        
        if is_verified==True:
            mod=get(guild.members, id=memberdict["staff_id"])
            
            if await self.config.guild(guild).enable_member_equal_id()==False:
                
                if memberrole and id_role in member.roles:
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). \n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). \n Method: {memberdict['verification_method']}.", ephemeral=True)
                else:
                    await member.add_roles(memberrole)
                    await member.add_roles(id_role)
                    await member.remove_roles(unverifiedrole)
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
            else:
                if memberrole in member.roles:
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). \n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). \n Method: {memberdict['verification_method']}.", ephemeral=True)
                else:
                    await member.add_roles(memberrole)
                    await member.remove_roles(unverifiedrole)
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
           
        elif is_verified== False and crossverified == None:
            
            await interaction.response.send_message(f"Your wish is my command, dear {author.name}. Proceeding with the verification...", ephemeral=True)
            await asyncio.sleep(1)
            # Add member, mod to the json
            ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            if comment == None:
                cmt = "No comment given."
            else:
                cmt = comment

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
            await self.config.guild(guild).users.set(user_logs)
            
            
            # Embed : Log
            log_title = "**Verification Procedure**"
            log_desc = f"{member.name} has been verified in our server."

            log_embed = discord.Embed(title= log_title, description = log_desc,color=clr)
            log_embed.add_field(name=f"**Member**", value=f"{member.mention} ({member.name})", inline=False)
            log_embed.add_field(name=f"**Member ID**", value=f"```{member.id}```", inline=True)
            log_embed.add_field(name=f"**Member Birth Date**", value=f"{birth_date}", inline=True)
            log_embed.add_field(name=f"**Staff Member**", value=f"{author.mention} ({author.name}, ```{author.id}```)", inline=False)
            log_embed.add_field(name=f"**Verification Method**", value="Member verified through ID", inline=False)
            log_embed.add_field(name=f"**Comments**", value=f"{cmt}", inline=False)
            log_embed.set_footer(text=f"Verification Date: {ts}")
            
            if await self.config.guild(guild).enable_verification_log():
                logmsg = await guild.get_channel(verificationlog.id).send(embed=log_embed)
            else:
                logmsg = await guild.get_channel(log.id).send(embed=log_embed)
            
            link = logmsg.jump_url
            dict_ = {
                "member_id" : member.id,
                "member_name" : member.name,
                "staff_name": author.name,
                "staff_id" : author.id,
                "verification_method": "Member verified through ID",
                "timestamp" : ts,
                "log_url": link,
                "log_id": logmsg.id,
                "birth_date" : birth_date,
                "comment" : cmt
                }
            
            verifications[member.id] = dict_
            await self.config.guild(guild).verified_users.set(verifications)
            
            # Remove unverified, and add member role / id-verified role
            if await self.config.guild(guild).enable_member_equal_id()==False:   
                await member.add_roles(memberrole)
                await member.add_roles(id_role)
                await member.remove_roles(unverifiedrole)
            else:
                await member.add_roles(memberrole)
                await member.remove_roles(unverifiedrole)
            
            
            # Embed : Welcome
            if welcome_message != None and welcome != None and await self.config.guild(guild).enable_welcome():
                str_welcome = f"{member.name} ({member.mention}) has just verified.\n" + welcome_message
                welcome_embed = discord.Embed(title="**Welcome to this new soul!**", 
                                            description=str_welcome, 
                                            color=clr)

                await guild.get_channel(welcome.id).send(embed = welcome_embed)
                
            # Embed : Ticket
            str_ticket = f"Welcome, {member.name}. As you have just finished verifying, you will be allowed to step into the realm of {guild.name}. For more information, consider looking around."
            ticket_embed =discord.Embed(title=f"**Welcome to {guild.name}!**", description=str_ticket, color=clr)
            await interaction.channel.send(embed=ticket_embed)
            
            if await self.config.guild(guild).enable_partner_verification():
                # Embed : DoB verif
                dob_string = f"**Verification** of {member.name}."
                dob_embed = discord.Embed(title="**Verifications: Server Partners**", description=dob_string, color=clr)
                dob_embed.add_field(name="Member", value=f"{member.mention} ({member.name})", inline=False)
                dob_embed.add_field(name="Member ID", value=f"```{member.id}```", inline=True)
                dob_embed.add_field(name="Member Birth Date", value=f"{birth_date}", inline=True)
                dob_embed.add_field(name="Verification Method", value=f"Member is ID-verified.", inline=True)
                dob_embed.add_field(name="Verified by", value=f"{author.mention} ({author.name}, ```{author.id}```)", inline=False)
                log_embed.set_footer(text=f"Verification Date: {ts}")
                await guild.get_channel(dob.id).send(embed=dob_embed)
                
            
            
            # Command used
            modlog_embed = discord.Embed(title= "**Command Usage**", description = f"verify by {author.name}",color=clr)
            await guild.get_channel(modlog.id).send(embed=modlog_embed)
            
        elif is_verified==False and crossverified != None:
            await interaction.response.send_message(f"Your wish is my command, dear {author.name}. Proceeding with the verification...", ephemeral=True)
            await asyncio.sleep(1)
            # Add member, mod to the json
            ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            if comment == None:
                cmt = "No comment given."
            else:
                cmt = comment

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
            await self.config.guild(guild).users.set(user_logs)
            
            
            # Embed : Log
            log_title = "**Verification Procedure**"
            log_desc = f"{member.name} has been crossverified in our server."

            cv = "Crossverification from" + f"{crossverified}"
            
            log_embed = discord.Embed(title= log_title, description = log_desc,color=clr)
            log_embed.add_field(name=f"**Member**", value=f"{member.mention} ({member.name})", inline=False)
            log_embed.add_field(name=f"**Member ID**", value=f"```{member.id}```", inline=True)
            log_embed.add_field(name=f"**Member Birth Date**", value=f"{birth_date}", inline=True)
            log_embed.add_field(name=f"**Staff Member**", value=f"{author.mention} ({author.name}, ```{author.id}```)", inline=False)
            log_embed.add_field(name=f"**Verification Method**", value=cv, inline=False)
            log_embed.add_field(name=f"**Comments**", value=f"{cmt}", inline=False)
            log_embed.set_footer(text=f"Verification Date: {ts}")
            
            if await self.config.guild(guild).enable_verification_log():
                logmsg = await guild.get_channel(verificationlog.id).send(embed=log_embed)
            else:
                logmsg = await guild.get_channel(log.id).send(embed=log_embed)
            
            link = logmsg.jump_url
            dict_ = {
                "member_id" : member.id,
                "member_name" : member.name,
                "staff_name": author.name,
                "staff_id" : author.id,
                "verification_method": cv,
                "timestamp" : ts,
                "log_url": link,
                "log_id": logmsg.id,
                "birth_date" : birth_date,
                "comment" : cmt
                }
            
            verifications[member.id] = dict_
            crossverifications[member.id] = dict_
            await self.config.guild(guild).crossverified_users.set(crossverifications)
            await self.config.guild(guild).verified_users.set(verifications)
            
            # Remove unverified, and add member role
                
            if await self.config.guild(guild).enable_member_equal_id()==False:   
                await member.add_roles(memberrole)
                await member.add_roles(id_role)
                await member.add_roles(crossverifiedrole)
                await member.remove_roles(unverifiedrole)
            else:
                await member.add_roles(memberrole)
                await member.add_roles(crossverifiedrole)
                await member.remove_roles(unverifiedrole)
            
            # Embed : Welcome
            if welcome_message != None and welcome != None and await self.config.guild(guild).enable_welcome():
                str_welcome = f"{member.name} ({member.mention}) has just verified.\n" + welcome_message
                welcome_embed = discord.Embed(title="**Welcome to this new soul!**", 
                                            description=str_welcome, 
                                            color=clr)
                await guild.get_channel(welcome.id).send(embed = welcome_embed)
                
            # Embed : Ticket
            str_ticket = f"Welcome, {member.name}. As you have just finished verifying, you will be allowed to step into the realm of {guild.name}. For more information, consider looking around."
            ticket_embed =discord.Embed(title=f"**Welcome to {guild.name}!**", description=str_ticket, color=clr)
            await interaction.channel.send(embed=ticket_embed)
            
            if await self.config.guild(guild).enable_partner_verification():
                # Embed : DoB verif
                dob_string = f"**Verification** of {member.name}."
                dob_embed = discord.Embed(title="**Verifications: Server Partners**", description=dob_string, color=clr)
                dob_embed.add_field(name="Member", value=f"{member.mention} ({member.name})", inline=False)
                dob_embed.add_field(name="Member ID", value=f"```{member.id}```", inline=True)
                dob_embed.add_field(name="Member Birth Date", value=f"{birth_date}", inline=True)
                dob_embed.add_field(name="Verification Method", value=f"{cv}", inline=True)
                dob_embed.add_field(name="Verified by", value=f"{author.mention} ({author.name}, ```{author.id}```)", inline=False)
                log_embed.set_footer(text=f"Verification Date: {ts}")
                await guild.get_channel(dob.id).send(embed=dob_embed)
                
            
            
            # Command used
            modlog_embed = discord.Embed(title= "**Command Usage**", description = f"verify by {author.name}",color=clr)
            await guild.get_channel(modlog.id).send(embed=modlog_embed)

    
    @commands.command()
    @commands.guild_only()
    async def enter(self, ctx):
        
        """ Allows you to enter the server. """
        
        
        # Basic I/O.
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        entry_cat = await self.config.guild(guild).entry_ticket_category()
        freshjoin = get(guild.roles, id = await self.config.guild(guild).freshjoin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        unverifiedrole = get(guild.roles, id = await self.config.guild(guild).unverified_role())
        
        modlog = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        log = get(guild.channels, id = await self.config.guild(guild).log_channel())


        if not await self.config.guild(guild).enable_verification():
            await ctx.send("My apologies, however, this feature is disabled. You are required to enable it, before commencing.")
            return
        elif staffrole == None or unverifiedrole == None or modlog == None or log == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if freshjoin != None:
            
            if entry_cat == None or await self.config.guild(guild).enable_entry() == False:
                return
            elif ctx.channel.category.id != entry_cat:
                return
            
            
            await asyncio.sleep(2)
            msg = await ctx.send(f"Your wish is my command, {author.name}. \n You have been assigned the role {unverifiedrole.mention}, while I unassigned {freshjoin.mention}. \n Please head over to the next section, which has now been unlocked.")
            
            await author.add_roles(unverifiedrole)
            await author.remove_roles(freshjoin)
            await asyncio.sleep(3)
            await msg.delete()
            await ctx.message.delete()
            log_embed = discord.Embed(title="**Member Entry:**", description=f"{author.mention} ({author.id} | {author.name}) has just entered the server and taken up the role {unverifiedrole.mention}. \n I assigned to them {unverifiedrole.mention}, and unassigned the previous role {freshjoin.mention}.", color=clr)
            log_embed.set_footer(text=f"Date: {ts}")
            await guild.get_channel(log.id).send(embed=log_embed) 
        else:
            await asyncio.sleep(2)
            entry_cat = await self.config.guild(guild).entry_ticket_category()
            if entry_cat == None or await self.config.guild(guild).enable_entry() == False:
                return
            elif ctx.channel.category.id != entry_cat:
                return
            await ctx.send(f"Your wish is my command, {author.name}. \n You have been assigned the role {unverifiedrole.mention}. \n Please head over to the next section, which has now been unlocked.")
            await asyncio.sleep(3)
            await author.add_roles(unverifiedrole)
            log_embed = discord.Embed(title="**Member Entry:**", description=f"{author.mention} ({author.id} | {author.name}) has just entered the server and taken up the role {unverifiedrole.mention}. \n I assigned to them {unverifiedrole.mention}.", color=clr)
            log_embed.set_footer(text=f"Date: {ts}")
            await guild.get_channel(log.id).send(embed=log_embed) 
 
    
    @commands.command()
    @commands.guild_only()
    async def codeword(self, ctx, codeword: str):
        
        """ Start the verification process (with the codeword). """
        
        # Basic I/O.
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        
        instructions = await self.config.guild(guild).instruction_message()
        introduction = await self.config.guild(guild).introduction_message()
        codeword_r = await self.config.guild(guild).codeword_rules()
        
        time_begin = datetime.datetime.now()
        x = datetime.datetime.now() - time_begin
        
        entry_cat = await self.config.guild(guild).entry_ticket_category()
        if entry_cat == None or self.config.guild(guild).enable_entry() == False:
            return
        elif ctx.channel.category.id != entry_cat:
            return
                
        if not await self.config.guild(guild).enable_codeword() or codeword == None:
            await ctx.send(f"This feature is not enabled.")
            return
        
        if codeword.lower() != codeword_r.lower():
            await ctx.send("My apologies, however, your entered **codeword** is incorrect. Please try again, by reading through the rules.")
            return
        
        await ctx.send("**Welcome to our Realm! You are required to verify before entering the server.**")
        await asyncio.sleep(5)
        while x.total_seconds() < 28800:
            time_now = datetime.datetime.now()
            x = time_begin - time_now
            await ctx.send(f"> Proceeding with the verification process...")
            await asyncio.sleep(4)
                    
            if await self.config.guild(guild).enable_introduction() and introduction != None:
                await ctx.send("> Please fill out the introduction as it is, **without leaving out any of the categories and their names.** Will be able to proceed in a bit...")
                await asyncio.sleep(5)
                embed = discord.Embed(title="**Introduction**",description=f"Simply copy using the button in the upper right (on PC), or copy and paste the message on mobile. \n ```{introduction}```", color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await ctx.send(embed=embed)
                await ctx.send(f'{introduction}')
                await asyncio.sleep(5)
                await ctx.send("> You may send the introduction now.")
                await asyncio.sleep(10)
                        
                try:
                    async with asyncio.timeout(300):
                        msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
                except TimeoutError:
                    await ctx.send(f"> You have taken too long to respond. Post your introduction again.")
                    return
                
                if msg.content == None:
                    return

                        
                await ctx.send(f"> **Congratulations!** Staff will check your introduction and give you the **O.K. afterwards**. \n> *Note*: We do not allow illegal kinks, such as NSFW ageplay (with age-regressed members), gore, vore, ... \n> Proceeding with the verification process...")
                await asyncio.sleep(8)
                        
                if await self.config.guild(guild).enable_instructions() and instructions != None:
                    embed = discord.Embed(title="**Instructions**",description=f"Follow the procedure as given below. \n"+instructions + "\n\nWill be able to proceed in a bit...", color=clr)
                    embed.set_footer(text="Date - {}".format(timestamp))
                    await ctx.send(embed=embed)
                    await asyncio.sleep(10)
                await ctx.send(f"> I have now fulfilled my duty. Staff will take over once one finds time to attend to your ticket.")
                return
            else:
                if await self.config.guild(guild).enable_introduction() and introduction == None:
                    await ctx.send(f"> I have now fulfilled my duty. Staff will take over once one finds time to attend to your ticket.")
                    return       
                elif await self.config.guild(guild).enable_introduction() == False:
                    pass
                        
                if await self.config.guild(guild).enable_instructions() and instructions != None:
                            embed = discord.Embed(title="**Instructions**",description=f"Follow the procedure as given below. \n"+instructions + "\n\nWill be able to proceed in 10 seconds...", color=clr)
                            embed.set_footer(text="Date - {}".format(timestamp))
                            await ctx.send(embed=embed)
                            await asyncio.sleep(10)
                await ctx.send(f"> I have now fulfilled my duty. Staff will take over once one finds time to attend to your ticket.")
                return
                            
    @commands.command()
    @commands.guild_only()
    async def introduce(self, ctx):
        
        """ Post the introduction template. """
        
        
        # Basic I/O.
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        unverifiedrole = get(guild.roles, id = await self.config.guild(guild).unverified_role())
        instructions = await self.config.guild(guild).instruction_message()
        introduction = await self.config.guild(guild).introduction_message()

        if not await self.config.guild(guild).enable_introduction():
            await ctx.send("My apologies, however, this feature is disabled. You are required to enable it, before commencing.")
            return
        if introduction == None:
            await ctx.send("My apologies, however, this feature is disabled. You are required to enable it, before commencing.")
            return
        
        await ctx.send(f"Below is the introduction template.")
        await ctx.send(f"{introduction}")
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def instructions(self, ctx):
        
        """ Post the verification instructions. """
        
        
        # Basic I/O.
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        instructions = await self.config.guild(guild).instruction_message()

        if not await self.config.guild(guild).enable_instructions():
            await ctx.send("My apologies, however, this feature is disabled. You are required to enable it, before commencing.")
            return
        if instructions == None:
            await ctx.send("My apologies, however, this feature is disabled. You are required to enable it, before commencing.")
            return
        
        await ctx.send(f"Below are the instructions for verification.")
        await ctx.send(f"{instructions}")

    
                
   

    
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
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        elif adminrole not in author.roles and modrole not in author.roles:
            if modrole in member.roles or adminrole in member.roles:
                await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                return
        elif modrole in author.roles and adminrole not in author.roles:
            if adminrole in member.roles:
                await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                return
            elif modrole in member.roles or staffrole in member.roles:
                is_staff = True
        elif modrole in author.roles or adminrole in author.roles:
            if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
                is_staff = True
        elif staffrole in member.roles:
            is_staff = True
        
        # Check the rest
        if reason == None:
            reason = "None given."
        
        if member == author:
            await ctx.send(f"My apologies, dear {author.name}, however, I can not allow you to kick yourself. Doing so amounts to a foolish action I will not tolerate. Behave yourself.")
            return
        elif member.id == 852263086714257440:
            await ctx.send(f"My apologies, dear {author.name}, I can not allow you to kick my creator.")
            return
        elif member.id == 1191841714504212490:
            await ctx.send(f"My apologies, dear {author.name}, I can not kick myself.")
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
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        quarantinerole = get(guild.roles, id = await self.config.guild(guild).quarantine_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        quarantine_channel = get(guild.channels, id = await self.config.guild(guild).quarantine_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or modlog_channel == None or quarantine_channel == None or quarantinerole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        elif adminrole not in author.roles and modrole not in author.roles:
            if modrole in member.roles or adminrole in member.roles:
                await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                return
        elif modrole in author.roles and adminrole not in author.roles:
            if adminrole in member.roles:
                await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                return
            elif modrole in member.roles or staffrole in member.roles:
                is_staff = True
        elif modrole in author.roles and adminrole in author.roles:
            if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
                is_staff = True
        elif staffrole in member.roles:
            is_staff = True
        
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
        
        for logs in quarantine_logs:
            if logs["member_id"] == member.id:
                logged_already = logs
        
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
                quarantine_logs.remove(logged_already)
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
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if staffrole not in author.roles:
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        elif adminrole not in author.roles and modrole not in author.roles:
            if modrole in member.roles or adminrole in member.roles:
                await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                return
        elif modrole in author.roles and adminrole not in author.roles:
            if adminrole in member.roles:
                await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                return
            elif modrole in member.roles or staffrole in member.roles:
                is_staff = True
        elif modrole in author.roles and adminrole in author.roles:
            if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
                is_staff = True
        elif staffrole in member.roles:
            is_staff = True
        
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
        is_staff = False
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif adminrole not in author.roles and modrole not in author.roles:
                if modrole in member.roles or adminrole in member.roles:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif modrole in author.roles and adminrole not in author.roles:
                if adminrole in member.roles:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
                elif modrole in member.roles or staffrole in member.roles:
                    is_staff = True
            elif modrole in author.roles and adminrole in author.roles:
                if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
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
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif adminrole not in author.roles and modrole not in author.roles:
                if modrole in member.roles or adminrole in member.roles:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif modrole in author.roles and adminrole not in author.roles:
                if adminrole in member.roles:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
                elif modrole in member.roles or staffrole in member.roles:
                    is_staff = True
            elif modrole in author.roles and adminrole in author.roles:
                if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
                    is_staff = True
        else:
            is_staff = False
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
            
        # Public mod enabled or not
        if await self.config.guild(guild).enable_public_mod() and public_mod_channel !=  None:
            
            for lgs in ban_logs:
                if lgs["member_id"] == member.id:
                    target_log = lgs
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
            try: 
                await guild.unban(member)
                if successful:
                    await ctx.send(f"Dear {author.name}, you have unbanned member {member.name}. I gave them notice of their fate")
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
        elif not await self.config.guild(guild).enable_public_mod() or public_mod_channel==None:
            
            for lgs in ban_logs:
                if lgs["member_id"] == member.id:
                    target_log = lgs
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
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        if member in guild.members:
            if staffrole not in author.roles:
                    await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                    return
            elif adminrole not in author.roles and modrole not in author.roles:
                    if modrole in member.roles or adminrole in member.roles:
                        await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                        return
            elif modrole in author.roles and adminrole not in author.roles:
                    if adminrole in member.roles:
                        await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                        return
                    elif modrole in member.roles or staffrole in member.roles:
                        is_staff = True
            elif modrole in author.roles and adminrole in author.roles:
                    if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
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
        
        # Get roles and channels
        modrole = get(guild.roles, id = await self.config.guild(guild).mod_role())
        adminrole = get(guild.roles, id = await self.config.guild(guild).admin_role())
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        log_channel = get(guild.channels, id = await self.config.guild(guild).log_channel())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        public_mod_channel = get(guild.channels, id = await self.config.guild(guild).public_moderation_channel())
        dm_bool = await self.config.guild(guild).enable_dm()
        # Check for cases where user / member are staff. Ensure hierarchy.
        if modrole == None or adminrole == None or staffrole== None or log_channel == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if member in guild.members:
            if staffrole not in author.roles:
                await ctx.send("My apologies, however, you need to be a staff member to use this command.")
                return
            elif adminrole not in author.roles and modrole not in author.roles:
                if modrole in member.roles or adminrole in member.roles:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
            elif modrole in author.roles and adminrole not in author.roles:
                if adminrole in member.roles:
                    await ctx.send("My apologies, however, you are not high enough in the hierarchy.", ephemeral=True)
                    return
                elif modrole in member.roles or staffrole in member.roles:
                    is_staff = True
            elif modrole in author.roles and adminrole in author.roles:
                if adminrole in member.roles or modrole in member.roles or staffrole in member.roles:
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
    
    
    
    
    
    
    
    
    
    