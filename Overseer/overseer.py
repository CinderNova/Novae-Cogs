import discord, json, random, asyncio, logging, traceback, redbot.core.data_manager, datetime, re
from redbot.core import commands, app_commands, utils
from redbot.core.bot import Red
from redbot.core.config import Config
from datetime import timedelta
from discord.utils import get

from .abc import MixinMeta, CompositeMetaClass
from .core.settings import Settings
from .core.moderation import Moderation
from .core.verification import Verification
from .core.comfort import Comfort


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

    



class overseer(commands.Cog, Settings, Moderation, Verification, Comfort, metaclass = CompositeMetaClass):
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
            "messagecount" : {},
            
            "enable_member_blacklist" : False,
            "enable_server_blacklist" : False,
            "enable_member_blacklist_auto_action" : False, 
            
            "enable_verification" : False,
            "enable_verify" : False,
            "enable_entry" : True,
            "enable_verification_log" : True,
            "enable_partner_verification" : False,
            "enable_unverified_role" : False,
            
            "enable_codeword" : False,
            "enable_instructions" : False,
            "enable_introduction" : False,
            "enable_welcome" : False,
            
            "enable_member_equal_id" : False,
            "enable_dm" : False,
            
            "enable_booster_log" : False,
            "enable_navigation" : False,
            
            "enable_quarantine" : True,
            "enable_public_mod" : True,
            "enable_threshold_action" : False,
            
            
            
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
            
            "welcome_message" : None,
            "codeword_rules" : None,
            "introduction_message" : None,
            "instruction_message" : None,
            
            "member_blacklist_auto_action" : None,
            "threshold_action" : "none",
            "warn_threshold" : 5,
            "incident_threshold" : 10,
            
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
            "top_role" : None,
            "verification_role" : None,
            "booster_role" : None,
            "unverified_role" : None,
            "crossverified_role" : None,
            "staff_role" : [],
            "freshjoin_role" : None,
            "serverpartner_role" : None,
            "quarantine_role" : None,
            "navigation_name" : "Navigator"
        }
        default_user = {}
        self.config.register_guild(**default_guild)
        self.config.register_user(**default_user)



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
        
        is_in = element_check(self, ctx, user_log, "member_id", member.id)
        
        if is_in[0]==False:
            target = None
        else:
            target = is_in[1]

        
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
            await self.config.guild(guild).users.set(user_log)


        action = await self.config.guild(guild).threshold_action()
        action = action.lower()
        # Check if enabled or disabled action, check which action it is
        if not await self.config.guild(guild).enable_threshold_action():
            return
        else:
            if action == "kick":
                reason = f"You have been kicked, as your warn or incident count has reached the threshold. You are not tolerated within {guild.name}."
                
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
                        await ctx.send(f"{member.name} has been kicked from {guild.name}, as their incident count reached the limit.")
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
                        await ctx.send(f"{member.name} has been kicked from {guild.name}, as their warn count reached the limit. ")
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
                        await ctx.send(f"{member.name} has been banned from {guild.name}, as their incident count reached the limit. ")
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
                        await ctx.send(f"{member.name} has been banned from {guild.name}, as their warn count reached the limit. ")
                    target["threshold"] = 0
            elif action == None:
                return
    

    
    @commands.Cog.listener()
    async def on_message(self, message):
        
        """ Implement the channel searching function. """
        guild = message.guild
        message_channel = message.channel
        content = message.content
        navigation_name = await self.config.guild(guild).navigation_name()
        author = message.author
        
        messagecount_tmp = await self.config.guild(guild).messagecount()
        
        if str(author.id) in messagecount_tmp:
            messagecount_tmp[str(author.id)][0] += 1
        else:
            messagecount_tmp[str(author.id)] = [1, 0]
        
        await self.config.guild(guild).messagecount.set(messagecount_tmp)
        
        if await self.config.guild(guild).enable_navigation():
            
            if content.startswith(navigation_name) and 'fetch me' in content:
                
                content = ''.join(word for word in content.split() if word not in [navigation_name, 'fetch me'])
                channellist = []
                
                for channel in guild.channels:
                    if channel.name[2:] in content.lower():
                        channellist.append(channel)
                await asyncio.sleep(1)
            
                if channellist == []:
                    await guild.get_channel(message_channel.id).send(f"My apologies, these channels do not exist.")
                else:
                    it = f"Dear {author.name}, I have found the following channels: "
                    for el in channellist:
                        it+= f"{el.mention} "
                    await guild.get_channel(message_channel.id).send(it)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        """ Check for blacklisted member on join. """
        
        guild = member.guild
        clr = 0xfffff
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        target = None
        
        channel = get(guild.channels, id=await self.config.guild(guild).staff_channel())
        staffrole = get(guild.roles, id= await self.config.guild(guild).staff_role())
        modlog = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        quarantinerole = get(guild.roles, id = await self.config.guild(guild).quarantine_role())
        
        if channel == None or staffrole == None or modlog == None or quarantinerole == None:
            return
        
        if await self.config.guild(guild).enable_member_blacklist_auto_action() == False:
            return
        

        action = await self.config.guild(guild).member_blacklist_auto_action()
        
        if action.lower() == "kick":
            blacklist = await self.config.guild(guild).member_blacklist()
            
            b_log = blacklist["log"]
            
            is_in = False
            for items in b_log:
                if items["member_id"] == member.id:
                    is_in = True
                    target = items
            
            if is_in == False:
                return
            
            
            
            content = target["reason"]
            # Quarantine the user or send a message.
            
            embed = discord.Embed(title="** Kick has been issued. **", description=f"**A blacklisted user has joined the server.** \n As the blacklist auto action has been set to 'kick', I will proceed to ping the Staff. \nThe following user, that is blacklisted, joined:", color=clr)
            embed.add_field(name=f"**User:**", value=f"{member.name} ({member.id})", inline=False)
            embed.add_field(name=f"**Reason:**", value=f"{content}", inline=False)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            # Get user, make sure there is existing log
            kick_log = await self.config.guild(guild).kick_logs()
            kick_logs = kick_log["logs"]
            incidents_logs = await self.config.guild(guild).incident_logs()
            user_logs = await self.config.guild(guild).users()
            
            target_new = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target_new = user_logs[keys]

            if target_new==None:
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
                target_new = user_logs[member.id]
            
            # Log embed
            log_embed = discord.Embed(title="**Moderation Action: Kick **", description=f"**Attention.** A user has been kicked in {guild.name}.", color=clr)
            log_embed.add_field(name="**Reason:**", value=content)
            log_embed.add_field(name="**by Staff**", value=f"Auto Action", inline=False)
            if member not in guild.members:
                log_embed.add_field(name="**User:**", value=f"{member.name} ({member.id})", inline=False)
            else:
                log_embed.add_field(name="**User:**", value=f"{member.mention} ({member.name} | {member.id})")
            log_embed.set_footer(text="Date - {}".format(timestamp))

            Goodbye = f"Attention, {member.mention}, \n you have been deemed suspicious or otherwise worthy of investigation within {guild.name} for your behaviour, thus you were kicked.\n My deepest apologies."
            # Post the log messages.
            log_message = await guild.get_channel(modlog.id).send(embed=log_embed)
            try:
                await member.send(Goodbye)
                successful = True
            except:
                successful = False
            
            
            
            
            number = len(target_new["kicks"]) + 1
            
            for_kick_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Akarin", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
                "number" : number
            }
            
            for_incident_log = {
                "incident_type" : "kick",
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Akarin", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "guild" : [guild.name, guild.id],
                "number" : number
            }

            await guild.get_channel(channel.id).send(embed=embed)
            
            try:
                kick_log["logs"].append(for_kick_log)
                incidents_logs["logs"].append(for_incident_log)
                target_new["kicks"].append(for_kick_log)
                target_new["threshold"] += 1
                
                user_logs[member.id] = target_new # Save the logs
                await self.config.guild(guild).kick_logs.set(kick_log)
                await self.config.guild(guild).incident_logs.set(incidents_logs)
                await self.config.guild(guild).users.set(user_logs)
            except:
                await guild.get_channel(channel.id).send(f"Penis")
                return
                
            try: 
                await guild.kick(member, reason=f"My apologies, you have been deemed unworthy of {guild.name}.")
            except:
                await guild.get_channel(channel.id).send(f"My apologies, however, I was not able to kick {member.name} ({member.mention}). There has been an error. Please attempt again, and contact my Creator.")
                return
            
        elif action.lower() == "ban":
            blacklist = await self.config.guild(guild).member_blacklist()
            b_log = blacklist["log"]
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
            target_new = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target_new = user_logs[keys]
            
            if target_new==None:
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
                target_new = user_logs[member.id]
            
                    
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
            
            number = len(target_new["bans"]) + 1
            
            for_ban_log = {
                "member_name" : member.name,
                "member_id" : member.id,
                "staff_id": 1152654636021448786,
                "staff_name" : "Themis", 
                "date" : timestamp,
                "reason" : content,
                "message_link" : log_message.jump_url,
                "server" : [guild.name,guild.id],
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
            target_new["bans"].append(for_ban_log)
            target_new["threshold"] += 1
            
            user_logs[member.id] = target_new
            
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
        elif action.lower() == "quarantine":
            
            blacklist = await self.config.guild(guild).member_blacklist()
            b_log = blacklist["log"]
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
            target_new = None
            logged_already = None
            for keys in user_logs:
                if user_logs[keys]["member_id"] == member.id:
                    target_new = user_logs[keys]
            
            for logs in quarantine_logs:
                if logs["member_id"] == member.id:
                    logged_already = logs
            
            if logged_already != None and quarantinerole in member.roles:
                await guild.get_channel(channel.id).send("This user is already quarantined.")

            if target_new == None:
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
            
            number = len(target_new["quarantines"]) + 1
            
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
            target_new["quarantines"].append(for_quarantine_log)
            target_new["threshold"] += 1
            
            # Manage the threshold, and set the user log back
            user_logs[member.id] = target_new
            
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
            b_log = blacklist["log"]
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
        elif action.lower() not in ["kick", "ban", "quarantine", "alert"] or action.lower() == "none":
            return

    @commands.Cog.listener()
    async def on_member_leave(self, member: discord.Member):
        
        """ Check whether or not a user left for the x-th time """
        
        clr = 0xfffff
        guild = member.guild
        
        messagecount_temp = await self.config.guild(guild).messagecount()
        
        staffrole = get(guild.roles, id= await self.config.guild(guild).staff_role())
        modlog = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        
        if member.id in messagecount_temp:
            if messagecount_temp[member.id][1] < 4:
                messagecount_temp[member.id][1] += 1
            else:
                if messagecount_temp[member.id][0] < 100:
                    reason = 'User has less than 100 messages and left the server more than 4 times.'
                    await guild.ban(member, reason=reason)
                    await guild.get_channel(modlog.id).send(f"{staffrole.mention}: User {member.name} has been banned from {guild.name}.\nReason: {reason}")
        else:
            messagecount_temp[member.id] = [1,0]
            
        await self.config.guild(guild).messagecount.set(messagecount_temp)            
        
