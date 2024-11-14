import discord, json, random, asyncio, logging, traceback, redbot.core.data_manager, datetime, re
from redbot.core import commands, app_commands, utils
from redbot.core.bot import Red
from redbot.core.config import Config
from datetime import timedelta
from discord.utils import get

from ..abc import MixinMeta, CompositeMetaClass

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

    


class Settings(MixinMeta):
    
    """
    Overseer Settings.
    """
    
    # OVERARCHING CATEGORIES
    @commands.group(name="overseer")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def overseer(self, ctx):
        """ The group of commands related to the overseer settings. """
    
    @overseer.group(name="partners")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def partners(self, ctx):
        
        """ Relating to partner servers. This includes adding, removing, showing and managing (reasons, managers, verification roles) of partner servers. """
    
    @overseer.group(name="moderation")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def moderation(self, ctx):
        """ Relating to moderation settings. This involves basic moderation like bans, kicks, etc. and logs, for example. """
    
    @overseer.group(name="verification")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def verification(self, ctx):
        """ Relating to verification settings. This includes, as an example, setting messages needed for verification. """
    
    @overseer.group(name="settings")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """ Relating to general settings. This includes enabling and disabling features, for example, and setting roles and channels. """
    
    @overseer.group(name="blacklists")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def blacklists(self, ctx):
        """ The group of commands related to managing the blacklist. """
    
    @overseer.group(name="boosting")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def boosting(self, ctx):
        """ The group of commands related to managing the booster list. """
    
 
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def features(self, ctx):
        """ Sends a complete list of features (of this plugin) that can be enabled or disabled. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        features = "The following are features that can be enabled / disabled: \n member_blacklist \n server_blacklist \n member_blacklist_auto_action \n verification \n entry \n verify \n verification_log \n partner_verification \n unverified_roling \n codeword \n instructions \n introduction \n welcome \n member_equal_id \n dm \n booster_logging \n navigation \n quarantine \n public_mod \n threshold_action"
        
        await ctx.send(features)
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx, feature: str, *,  bools: str,):
        """ Enable or disable features of the bot. The format is enable [feature] [true or false]."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()

        if feature.lower() == "debug" and (await Red.is_owner(self.bot, author)):
            # Enable or disable debugging. (Bot-owner only)
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_debug.set(True)
                await ctx.send("You have enabled debugging.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_debug.set(False)
                await ctx.send("You have disabled debugging.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
                
        elif feature.lower() == "member_blacklist":
            # Enable or disable the member blacklist.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_member_blacklist.set(True)
                await ctx.send("You have enabled the member blacklist.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_member_blacklist.set(False)
                await ctx.send("You have disabled the member blacklist.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "server_blacklist":
            # Enable or disable the server blacklist.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_server_blacklist.set(True)
                await ctx.send("You have enabled the server blacklist.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_server_blacklist.set(False)
                await ctx.send("You have disabled the server blacklist.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "member_blacklist_auto_action":
            # Enable or disable the member blacklist auto action.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_member_blacklist_auto_action.set(True)
                await ctx.send("You have enabled the member blacklist automatic action.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_member_blacklist_auto_action.set(False)
                await ctx.send("You have disabled the member blacklist automatic action.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "verification":
            # Enable or disable the member blacklist.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_verification.set(True)
                await ctx.send("You have enabled verification.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_verification.set(False)
                await ctx.send("You have disabled verification.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")

        elif feature.lower() == "verify":
            # Enable or disable verify.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_verify.set(True)
                await ctx.send("You have enabled verify.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_verify.set(False)
                await ctx.send("You have disabled verify.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "entry":
            # Enable or disable entry.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_entry.set(True)
                await ctx.send("You have enabled entry.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_entry.set(False)
                await ctx.send("You have disabled entry.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "verification_log":
            # Enable or disable verification log.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_verification_log.set(True)
                await ctx.send("You have enabled the verification log.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_verification_log.set(False)
                await ctx.send("You have disabled the verification log.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "partner_verification":
            # Enable or disable the partner verification log.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_partner_verification.set(True)
                await ctx.send("You have enabled the partner verification log.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_partner_verification.set(False)
                await ctx.send("You have disabled the partner verification log.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "unverified_role":
            # Enable or disable the unverified roling.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_unverified_role.set(True)
                await ctx.send("You have enabled the unverified roling.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_unverified_role.set(False)
                await ctx.send("You have disabled the unverified roling.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "codeword":
            # Enable or disable the codeword.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_codeword.set(True)
                await ctx.send("You have enabled the codeword.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_codeword.set(False)
                await ctx.send("You have disabled the codeword.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "instructions":
            # Enable or disable instructions.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_instructions.set(True)
                await ctx.send("You have enabled verification instructions.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_instructions.set(False)
                await ctx.send("You have disabled verification instructions.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "introduction":
            # Enable or disable the introduction.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_introduction.set(True)
                await ctx.send("You have enabled the introduction.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_introduction.set(False)
                await ctx.send("You have disabled the introduction.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")

        elif feature.lower() == "welcome":
            # Enable or disable the welcome.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_welcome.set(True)
                await ctx.send("You have enabled the welcome.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_welcome.set(False)
                await ctx.send("You have disabled the welcome.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")

        elif feature.lower() == "member_equal_id":
            # Enable or disable whether or not the member role is equivalent to the ID role.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_member_equal_id.set(True)
                await ctx.send("You have enabled that the member role equals the ID role.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_member_equal_id.set(False)
                await ctx.send("You have disabled that the member role equals the ID role.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "dm":
            # Enable or disable DMs.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_dm.set(True)
                await ctx.send("You have enabled DMs.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_dm.set(False)
                await ctx.send("You have disabled DMs.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")

        elif feature.lower() == "booster_logging":
            # Enable or disable booster logging.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_booster_log.set(True)
                await ctx.send("You have enabled booster logging.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_booster_log.set(False)
                await ctx.send("You have disabled booster logging.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "navigation":
            # Enable or disable navigation.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_navigation.set(True)
                await ctx.send("You have enabled navigation.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_navigation.set(False)
                await ctx.send("You have disabled navigation.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "quarantine":
            # Enable or disable quarantine.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_quarantine.set(True)
                await ctx.send("You have enabled quarantine.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_quarantine.set(False)
                await ctx.send("You have disabled quarantine.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "public_mod":
            # Enable or disable public moderation logging.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_public_mod.set(True)
                await ctx.send("You have enabled public moderation logging.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_public_mod.set(False)
                await ctx.send("You have disabled public moderation logging.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        elif feature.lower() == "threshold_action":
            # Enable or disable the threshold action.
            if bools.lower() in ["true", "on", "enable", "enabled", "yes"]:
                await self.config.guild(guild).enable_threshold_action.set(True)
                await ctx.send("You have enabled public the threshold action.")
            elif bools.lower() in ["false", "disable", "disabled", "no", "off"]:
                await self.config.guild(guild).enable_threshold_action.set(False)
                await ctx.send("You have disabled threshold_action.")
            else:
                await ctx.send("You must enter a valid truth value, true or false.")
        
        else:
            await ctx.send("You need to enter an existing feature, or you do not have the necessary permissions.")

    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def msgleavecount(self, ctx, member: discord.User):
        """ Find the message count and leave count of a user. """
        guild = ctx.guild
        clr = await ctx.embed_colour()
        messagecount_temp = await self.config.guild(guild).messagecount()
        
        if str(member.id) in messagecount_temp:
            member_msg = messagecount_temp[str(member.id)][0]
            member_leave = messagecount_temp[str(member.id)][1]
        else:
            messagecount_temp[str(member.id)] = [1,0]
            member_msg = messagecount_temp[str(member.id)][0]
            member_leave = messagecount_temp[str(member.id)][1]    

        await ctx.send(f"Member {member.name} has {member_msg} message(s) in the server. \nThey left {member_leave} time(s).")
        
    # CHANNELS AND ROLES
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def channels(self, ctx, option: str, channel: discord.TextChannel):
        """ Set the channels needed for overseer. Possible options are: [quarantine, modlog, log, map, staff, boost, verification_log, partner_verification, welcome, public_mod]."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'channels' sub-command of 'overseer settings' command.")
            return
        
        # Determine all the possible channel calls.
        if option.lower() == "quarantine":
            # The option is the channel you want to set.
            await self.config.guild(guild).quarantine_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the quarantine channel to {channel.mention}, {author.name}.")

        elif option.lower() == "modlog":
            # The option is the channel you want to set.
            await self.config.guild(guild).modlog_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the mod log channel to {channel.mention}, {author.name}.")

        elif option.lower() == "log":
            # The option is the channel you want to set.
            await self.config.guild(guild).log_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the log channel to {channel.mention}, {author.name}.")
            
        elif option.lower() == "map":
            # The option is the channel you want to set.
            await self.config.guild(guild).map_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the map channel to {channel.mention}, {author.name}.")

        elif option.lower() == "staff":
            # The option is the channel you want to set.
            await self.config.guild(guild).staff_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the staff channel to {channel.mention}, {author.name}.")

        elif option.lower() == "boost":
            # The option is the channel you want to set.
            await self.config.guild(guild).boost_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the boost channel to {channel.mention}, {author.name}.")

        elif option.lower() == "verification_log":
            # The option is the channel you want to set.
            await self.config.guild(guild).verification_log_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the verification log channel to {channel.mention}, {author.name}.")

        elif option.lower() == "partner_verification":
            # The option is the channel you want to set.
            await self.config.guild(guild).partner_verification_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the partner verification log channel to {channel.mention}, {author.name}.")

        elif option.lower() == "welcome":
            # The option is the channel you want to set.
            await self.config.guild(guild).welcome_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the welcome channel to {channel.mention}, {author.name}.")

        elif option.lower() == "public_mod":
            # The option is the channel you want to set.
            await self.config.guild(guild).public_moderation_channel.set(channel.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the public moderation channel to {channel.mention}, {author.name}.")

        else:
            await ctx.send("You need to enter a valid option and / or text channel for this to work.")
            return
        
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def roles(self, ctx, option: str, role: discord.Role):
        """ Set the roles needed for overseer. Options are: [member, verification, booster, unverified, crossverified, freshjoin, serverpartner, quarantine, staff]."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'roles' sub-command of 'overseer settings' command.")
            return
        
        # Determine all possible roles calls.
        if option.lower() == "member":
            # Set the respective role..
            await self.config.guild(guild).member_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the member role to {role.mention}, {author.name}.")

        elif option.lower() == "top_role":
            # Set the respective role..
            await self.config.guild(guild).top_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the role above custom roles to {role.mention}, {author.name}.")
        
        elif option.lower() == "verification":
            # Set the respective role..
            await self.config.guild(guild).verification_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the ID-verified role to {role.mention}, {author.name}.")
        
        elif option.lower() == "booster":
            # Set the respective role..
            await self.config.guild(guild).booster_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the booster role to {role.mention}, {author.name}.")

        elif option.lower() == "unverified":
            # Set the respective role..
            await self.config.guild(guild).unverified_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the unverified role to {role.mention}, {author.name}.")

        elif option.lower() == "crossverified":
            # Set the respective role..
            await self.config.guild(guild).crossverified_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the crossverified role to {role.mention}, {author.name}.")
        
        elif option.lower() == "staff":
            # Set the respective role..
            await self.config.guild(guild).staff_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the staff role to {role.mention}, {author.name}.")
            
        elif option.lower() == "freshjoin":
            # Set the respective role..
            await self.config.guild(guild).freshjoin_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the freshly joined role to {role.mention}, {author.name}.")

        elif option.lower() == "serverpartner":
            # Set the respective role..
            await self.config.guild(guild).serverpartner_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the server partner role to {role.mention}, {author.name}.")

        elif option.lower() == "quarantine":
            # Set the respective role..
            await self.config.guild(guild).quarantine_role.set(role.id)
        
            # Print the message, if successful.
            await ctx.send(f"You have successfully set the quarantine role to {role.mention}, {author.name}.")

        else:
            await ctx.send("You need to enter a valid option and / or role.")
            return

        # THRESHOLDS AND THRESHOLD ACTIONS
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def warn_threshold(self, ctx, threshold: int):
        """ Set the warning threshold to a positive(!) number. \n
        Once a member reaches the threshold, they will automatically be punished."""
        
        guild = ctx.guild

        if threshold <= 0:
            await ctx.send(f"The warning threshold needs to be a strictly positive number. Please enter a number bigger than zero.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'warn_threshold' sub-command of 'moderation' command.")
            return
        
        await self.config.guild(guild).warn_threshold.set(threshold)
        await ctx.send(f"You have set the warning threshold to {threshold}.")

    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def incident_threshold(self, ctx, threshold: int):
        """ Set the incident threshold to a positive number. \n
        Once a member reaches the threshold, they will automatically be kicked. """
        
        guild = ctx.guild
        
        if threshold <= 0:
            await ctx.send(f"The warning threshold needs to be a strictly positive number. Please enter a number bigger than zero.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'incident_threshold' sub-command of 'moderation' command.")
            return
        
        await self.config.guild(guild).incident_threshold.set(threshold)
        await ctx.send(f"You have set the incident threshold to {threshold}.")
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def threshold_action(self, ctx, threshold_action: str):
        """ Set the threshold action. \n
        Once a member reaches either of the thresholds, they will be punished. \n
        Options are kick, ban, or nothing. \n
        Leave empty if you want nothing to happen."""
        
        guild = ctx.guild

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'threshold_action' sub-command of 'moderation' command.")
            return
        
        if threshold_action.lower() in ["kick", "kicking", "kicked", "kicks"]:
            await self.config.guild(guild).threshold_action.set("kick")
            await ctx.send(f"You have successfully set the threshold action to {threshold_action}. Users reaching the threshold will now be kicked.")
        elif threshold_action.lower() in ["ban", "banning", "banned", "bans"]:
            await self.config.guild(guild).threshold_action.set("ban")
            await ctx.send(f"You have successfully set the threshold action to {threshold_action}. Users reaching the threshold will now be banned.")
        elif threshold_action.lower() in ["none", "nothing"]:
            await self.config.guild(guild).threshold_action.set("none")
            await ctx.send(f"You have successfully set the threshold action to {threshold_action}. Nothing will happen once users reach the threshold.")
        else:
            await ctx.send(f"You need to set a specific action. You can choose from ban, kick or none.")
            return
    
    # VERIFICATION SETTINGS  
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def welcome_message(self, ctx, *, welcome_message: str):
        """ Set the welcome message. \n 
        This message will be sent into the [welcome] channel previously set, to greet a user after verifying. """
        
        guild = ctx.guild
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'welcome_message' sub-command of 'verification' command.")
            return
        
        await self.config.guild(guild).welcome_message.set(welcome_message)
        await ctx.send(f"You have set the welcome message to: \n {welcome_message}")
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def set_codeword(self, ctx, *, codeword: str):
        """ Set the codeword. \n 
        This codeword is required for users to enter in the verification process. """
        
        guild = ctx.guild
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'codeword' sub-command of 'verification' command.")
            return
        
        await self.config.guild(guild).codeword_rules.set(codeword)
        await ctx.send(f"You have set the codeword to: \n{codeword}")
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def introduction(self, ctx, *, introduction: str=None):
        """ Set the introduction template. \n
        Leave empty otherwise. """
        
        guild = ctx.guild
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'introduction' sub-command of 'verification' command.")
            return
        
        if introduction == None:
            introduction_ = "None set."
        else:
            introduction_ = introduction
        
        await self.config.guild(guild).introduction_message.set(introduction_)
        await ctx.send(f"You have set the introduction template to: \n {introduction_}")
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def instruction_message(self, ctx, *, instructions: str):
        """ Set verification instructions. \n
        They can be sent using a specific command. """
        
        guild = ctx.guild

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'instruction_message' sub-command of 'verification' command.")
            return
        
        await self.config.guild(guild).instruction_message.set(instructions)
        await ctx.send(f"You have set the instruction message to: \n {instructions}")

        # BLACKLISTS:
    
    @blacklists.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def addoption(self, ctx, option: str, name, *, reason: str=None):
        """ Add / remove [servers / members] to / from the respective blacklist. \n
        You need to use the user ID for users, and names for servers. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'addoption' sub-command of 'overseer settings blacklists' command.")
            return
        
        if option.lower() in ["member", "members"]:
            
            try:
                name = await self.bot.fetch_user(name)
            except:
                await ctx.send("You must enter a valid User ID.")
                return

            if reason == None:
                reason = "None"
            
            # Find the member blacklist, and figure out if the user is already blacklisted.
            member_blacklist = await self.config.guild(guild).member_blacklist()
            
            is_in = element_check(self, ctx, member_blacklist["log"], "member_id", name.id)
            
            if is_in[0] == True:
                sought_item = is_in[1]
                await ctx.send("This member is already blacklisted. Do you want to remove them?")
                
                try:
                    async with asyncio.timeout(150):
                        msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
                except TimeoutError:
                    await ctx.send("You have taken too long to respond.")
                    return
                
                if "no" in msg.content.lower():
                    await ctx.send("Then they will not be removed.")
                    return
                
                elif "yes" in msg.content.lower() or "yep" in msg.content.lower():
                    member_blacklist["log"].remove(sought_item)
                    await ctx.send(f"You have removed *{name.name}* from the member blacklist.")
                    await self.config.guild(guild).member_blacklist.set(member_blacklist)
                    return
        
            member_blacklist["log"].append({
                            "member_id" :   name.id, 
                            "member_name":  name.name,
                            "reason" : reason
                        })
        
            await self.config.guild(guild).member_blacklist.set(member_blacklist)

            # Print the message, if successful.
            await ctx.send(f"You have added *{name.name} ({name.id})* to the member blacklist, {author.name}. \n*Reason: {reason}*")
        
        elif option.lower() in ["server", "servers"]:

            if reason == None:
                reason = "None"
            
            if type(name) != type("Hello World"):
                await ctx.send("You must enter a server name.")
                return
            
            # Find the server blacklist, and figure out if the user is already blacklisted.
            server_blacklist = await self.config.guild(guild).server_blacklist()

            is_in = element_check(self, ctx, server_blacklist["log"], "server_name", name)
            
            if is_in[0] == True:
                sought_item = is_in[1]
                await ctx.send("This server is already blacklisted. Do you want to remove it?")
                try:
                    async with asyncio.timeout(150):
                        msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
                except TimeoutError:
                    await ctx.send("You have taken too long to respond.")
                    return
                
                if "no" in msg.content.lower():
                    await ctx.send("Then it will not be removed.")
                    return
                elif "yes" in msg.content.lower() or "yep" in msg.content.lower():
                    server_blacklist["log"].remove(sought_item)
                    await ctx.send(f"You have removed *{name}* from the server blacklist.")
                    await self.config.guild(guild).server_blacklist.set(server_blacklist)
                    return
        
            server_blacklist["log"].append({
                            "server_name":  name,
                            "reason" : reason
                        })
        
            await self.config.guild(guild).server_blacklist.set(server_blacklist)

            # Print the message, if successful.
            await ctx.send(f"You have added *{name}* to the server blacklist, {author.name}. \n*Reason: {reason}*")
        
        else:
            await ctx.send("You need to choose between the server blacklist or the member blacklist.")
            return
        
    @blacklists.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def checkoption(self, ctx, option: str, name, *, reason: str=None):
        """ Check whether or not a [server / member] is in the blacklist. \n
        You need to use the ID for users, and the name for servers. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'checkoption' sub-command of 'overseer settings blacklists' command.")
            return
        
        if option.lower() in ["member", "members"]:
            
            try:
                name = await self.bot.fetch_user(name)
            except:
                await ctx.send("You must enter a valid User ID.")
                return

            if reason == None:
                reason = "None"
            
            # Find the member blacklist, and figure out if the user is already blacklisted.
            member_blacklist = await self.config.guild(guild).member_blacklist()

            is_in = element_check(self, ctx, member_blacklist["log"], "member_id", name.id)
            
            if is_in[0] == True:
                sought_item = is_in[1]
                await ctx.send(f"This member is indeed blacklisted. Reason: \n{sought_item['reason']} \nDo you want to change the reason?")
                try:
                    async with asyncio.timeout(150):
                        msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
                except TimeoutError:
                    await ctx.send("You have taken too long to respond.")
                    return
                
                old_reason = sought_item["reason"]
                
                if "no" in msg.content.lower():
                    await ctx.send("Then it will stay unchanged.")
                    return
                elif "yes" in msg.content.lower() or "yep" in msg.content.lower():
                    await ctx.send("Please enter the new reason. ")
                    try:
                        async with asyncio.timeout(60):
                            message = await self.bot.wait_for("message", check=lambda message: message.author == author)
                    except TimeoutError:
                        await ctx.send("You have taken too long to respond. The reason has not been changed.")
                        return
                    member_blacklist["log"].remove(sought_item)
                    sought_item["reason"] = message.content
                    
                                   
                    member_blacklist["log"].append(sought_item)
                    await self.config.guild(guild).member_blacklist.set(member_blacklist)
                    await ctx.send(f"You have changed the reason behind *{name.name}* being blacklisted.\nOld reason: {old_reason}\nNew reason: {message.content}")
                    return
            else:
                await ctx.send("This member is not blacklisted.")
                return
        
        elif option.lower() in ["server", "servers"]:
            
            if reason == None:
                reason = "None"
            
            if type(name) != type("Hello World"):
                await ctx.send("You must enter a server name.")
                return
            
            # Find the server blacklist, and figure out if the server is blacklisted.
            server_blacklist = await self.config.guild(guild).server_blacklist()

            is_in = element_check(self, ctx, server_blacklist["log"], "server_name", name)
            
            if is_in[0] == True:
                sought_item = is_in[1]
                await ctx.send(f"This server is indeed blacklisted. Reason: \n{sought_item['reason']} \nDo you want to change the reason?")
                try:
                    async with asyncio.timeout(150):
                        msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
                except TimeoutError:
                    await ctx.send("You have taken too long to respond.")
                    return
                
                old_reason = sought_item["reason"]
                
                if "no" in msg.content.lower():
                    await ctx.send("Then the reason stays unchanged.")
                    return
                elif "yes" in msg.content.lower() or "yep" in msg.content.lower():
                    
                    await ctx.send("Please enter the new reason. ")
                    
                    try:
                        async with asyncio.timeout(60):
                            message = await self.bot.wait_for("message", check=lambda message: message.author == author)
                    except TimeoutError:
                        await ctx.send("You have taken too long to respond. The reason has not been changed.")
                        return
                    
                    server_blacklist["log"].remove(sought_item)
                    sought_item["reason"] = message.content
                    server_blacklist["log"].append(sought_item)
                    
                    await self.config.guild(guild).server_blacklist.set(server_blacklist)
                    await ctx.send(f"You have changed the reason behind *{name}* being blacklisted.\nOld reason: {old_reason}\nNew reason: {message.content}")
                    return
            else:
                await ctx.send("This server is not blacklisted.")
                return

        else:
            await ctx.send("You need to choose between the server blacklist or the member blacklist.")
            return
        
    @blacklists.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def clearoption(self, ctx, option: str, clear: str):
        """ Clear the [servers / members] blacklist. \n 
        You should write 'clearoption [option] [name] clear'. \n
        Possible options: server, member, all. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clearoption' sub-command of 'overseer settings blacklists' command.")
            return
        
        if option.lower() in ["member", "members"]:

            if "clear" not in clear.lower():
                await ctx.send("You need to append [clear] at the end of the command.")
                return
            
            # Find the member blacklist, and figure out if the user is already blacklisted.
            blacklist_default = {
                                "log" : []
                                }
        
            await self.config.guild(guild).member_blacklist.set(blacklist_default)

            # Print the message, if successful.
            await ctx.send(f"You have cleared the member blacklist, {author.name}.")
        
        elif option.lower() in ["server", "servers"]:
            
            if "clear" not in clear.lower():
                await ctx.send("You need to append [clear] at the end of the command.")
                return
            
            # Find the member blacklist, and figure out if the user is already blacklisted.
            blacklist_default = {
                                "log" : []
                                }
        
            await self.config.guild(guild).server_blacklist.set(blacklist_default)

            # Print the message, if successful.
            await ctx.send(f"You have cleared the server blacklist, {author.name}.")
        
        elif option.lower() in ["all", "both"]:
            
            if "clear" not in clear.lower():
                await ctx.send("You need to append [clear] at the end of the command.")
                return
            
            # Find the member blacklist, and figure out if the user is already blacklisted.
            blacklist_default = {
                                "log" : []
                                }
        
            await self.config.guild(guild).member_blacklist.set(blacklist_default)
            await self.config.guild(guild).server_blacklist.set(blacklist_default)

            # Print the message, if successful.
            await ctx.send(f"You have cleared the member and server blacklist, {author.name}.")
        
        else:
            await ctx.send("You need to choose between the server or member blacklist, or both.")
            return
        
    @blacklists.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def auto_action(self, ctx, action: str=None):
        """ Set an automatic action that will be applied when a blacklisted member joins. \n 
        You should write 'auto_action [action]'. \n
        Possible options: kick, ban, quarantine, alert, nothing (or leaving it empty). """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'auto_action' sub-command of 'overseer settings blacklists' command.")
            return
        
        # Sets the automatic action, depending on the choice.
        if action == None:
            action = "None"
            
        if action.lower() in ["kicks", "kick", "kicking"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("kick")
            await ctx.send(f"You have set the automatic action for blacklisted members to [kick]. \nMembers will be kicked if they are blacklisted and join the guild.")
            
        elif action.lower() in ["bans", "ban", "banning"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("ban")
            await ctx.send(f"You have set the automatic action for blacklisted members to [ban]. \nMembers will be banned if they are blacklisted and join the guild.")
            
        elif action.lower() in ["alert", "alerts", "alerting", "warning"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("alert")
            await ctx.send(f"You have set the automatic action for blacklisted members to [alert]. \nStaff will be alerted if blacklisted members join the guild.")
            
        elif action.lower() in ["quarantines", "quarantine", "quarantining", "quarantined"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("quarantine")
            await ctx.send(f"You have set the automatic action for blacklisted members to [quarantine]. \nMembers will be quarantined if they are blacklisted and join the guild.")
            
        elif action.lower() in ["none", "nothing", "nil", "zero"]:
            await self.config.guild(guild).member_blacklist_auto_action.set("quarantine")
            await ctx.send(f"You have set the automatic action for blacklisted members to [Nothing]. \nNothing will be done when a blacklisted member joins the guild.")
            
        else:
            await ctx.send(f"You need to enter valid options for the automatic action. \nOptions are: kick, ban, quarantine, alert, nothing (or leave it empty).")
            return
        
    @blacklists.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def showlist(self, ctx, option: str):
        """ Show the server blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'showlist' sub-command of 'overseer settings blacklist' command.")
            return
        
        if option.lower() in ["member", "members"]:
            
            # Set the blacklist.
            member_blacklist = await self.config.guild(guild).member_blacklist()
        
            printmessage = "**Here is the member blacklist:** \n"
            blacklist = member_blacklist["log"]
        
            if blacklist == []:
                printmessage += "The blacklist is currently empty."
                await ctx.send(printmessage)
            else:
                all_embeds = []
                pagination_items = 8
                    
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
                                reason = individ["reason"]
                                embed.description += f"```Member Name:       {member_name}\nMember ID:       {member_id}\nReason:       {reason}```\n"
                    else:
                        for individ in blacklist[offset : offset+pagination_items]:
                                member_name = individ["member_name"]
                                member_id = individ["member_id"]
                                reason = individ["reason"]
                                embed.description += f"```Member Name:       {member_name}\nMember ID:       {member_id}\nReason:       {reason}```\n"
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

        elif option.lower() in ["server", "servers"]:
            
            # Set the blacklist.
            server_blacklist = await self.config.guild(guild).server_blacklist()
        
            printmessage = "**Here is the server blacklist:** \n"
            blacklist = server_blacklist["log"]
        
            if blacklist == []:
                printmessage += "The blacklist is currently empty."
                await ctx.send(printmessage)
            else:
                all_embeds = []
                pagination_items = 8
                    
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
                                server_name = individ["server_name"]
                                reason = individ["reason"]
                                embed.description += f"```Server Name:       {server_name}\nReason:       {reason}```\n"
                    else:
                        for individ in blacklist[offset : offset+pagination_items]:
                                server_name = individ["server_name"]
                                reason = individ["reason"]
                                embed.description += f"```Server Name:       {server_name}\nReason:       {reason}```\n"
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

        else:
            await ctx.send("You need to choose between the server or member blacklist.")
            return
    
    
    
    
    # SERVER PARTNER COMMANDS
    
    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def addserver(self, ctx, rep: discord.User, *, partner_server: str):
        
        """ Add partner server to the list with a representative. \n
        Manager will be whoever entered the command. You need to enter a server ID, then the user ID. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "addserver", "Running 'addserver' sub-command of 'overseer partners' command.")
            return
        
        timestate = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        partners = await self.config.guild(guild).server_partners()
        
        is_in = element_check(self, ctx, partners, "server_name", partner_server)
            
        if is_in[0] == True:
            sought_item = is_in[1]
            await ctx.send("This server is already in the partner list. Do you want to remove it?")
            
            try:
                async with asyncio.timeout(150):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
                
            if "no" in msg.content.lower():
                await ctx.send("Then it will not be removed.")
                return
                
            elif "yes" in msg.content.lower() or "yep" in msg.content.lower():
                partners.pop(partner_server)
                await ctx.send(f"You have removed *{partner_server}* from the partner server list.")
                await self.config.guild(guild).server_partners.set(partners)
                return
        else:
            partners[partner_server] = {
                "server_name" : partner_server.lower(),
                "server_rep" : [rep.name, rep.id],
                "manager" : [author.name, author.id],
                "time" : timestate,
                "verifiedrole" : None
            }

            await self.config.guild(guild).server_partners.set(partners)
            
            # Log embed
            embed = discord.Embed(title="**Partner Servers**", description=f"A partner server has been added to the list.", color=clr)
            embed.add_field(name="Server Name", value=f"{partner_server}")
            embed.add_field(name="Server Rep", value=f"{rep.mention} ({rep.name} | ```{rep.id}```)", inline=False)    
            embed.add_field(name="Server Manager", value=f"{author.mention} ({author.name} | ```{author.id}```)", inline=False)    
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestate))
            await ctx.send(embed=embed)

    @partners.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def change(self, ctx, option: str, *, server: str, secondoption):
        
        """ Change the Server Partner Representative, the Manager, or the partner server's verified role. """
        
        
        guild = ctx.guild
        partners = await self.config.guild(guild).server_partners()
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "change", "Running 'change' sub-command of 'overseer partners' command.")
            return
        
        timestate = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        
        
        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole == None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        is_in = element_check(self, ctx, partners, "server_name", server)
        
        if is_in[0] == False or is_in[1] == None:
            await ctx.send("You are not partnered with this server.")
            return
        
        server_item = is_in[1]
        
        if option.lower() in ["rep", "representative"]:
            
            if type(secondoption) == type(author):
                server_item["rep"] = [secondoption.name, secondoption.id]
                partners[server] = server_item
                await self.config.guild(guild).server_partners.set(partners)
                await ctx.send(f"You have set the new partner representative to {secondoption.name}.")
            else:
                await ctx.send("You need to enter the representative through @[..name..].")
                return
            
        elif option.lower() in ["manager", "managers", "partnermanager"]:
            
            if type(secondoption) == type(author):
                server_item["manager"] = [secondoption.name, secondoption.id]
                partners[server] = server_item
                await self.config.guild(guild).server_partners.set(partners)
                await ctx.send(f"You have set the new partner server manager to {secondoption.name}.")
            else:
                await ctx.send("You need to enter the manager through @[..name..].")
                return
            
        elif option.lower() in ["role", "verifiedrole"]:
            
            if type(secondoption) == type(""):
                server_item["verifiedrole"] = secondoption
                partners[server] = server_item
                await self.config.guild(guild).server_partners.set(partners)
                await ctx.send(f"You have set the partner server's verified role to {secondoption}.")
            else:
                await ctx.send("You need to enter the name(!) of the verified role.")
                return
            
        else:
            await ctx.send("You need to choose out of manager, rep, or verifiedrole.")
            return
            
    @app_commands.command(description="View all current server partnerships.")
    @app_commands.guild_only()
    async def server_partners(self, interaction: discord.Interaction):

        """ View the partner server list. """
        
        author = interaction.user
        guild = interaction.guild
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        clr = 0xffffff

        
        partner = await self.config.guild(guild).server_partners()
        partners = list(partner.values())
        
        if partners:
            all_embeds = []
            pagination_items = 8
                
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
                        rep_name = individ["rep"][0]
                        rep_id = individ["rep"][1]
                        manager_name = individ["manager"][0]
                        manager_id = individ["manager"][1]
                        role = individ["verifiedrole"]
                        if role == None:
                            role = "Unknown."
                        date = individ["time"]
                        embed.description += f"Server: {server_name} \nRepresentative: {rep_name} ```{rep_id}```\nManager: {manager_name} ```{manager_id}```\nVerification Role: {role} \nDate of Establishment: {date}"
                else:
                    for individ in partners[offset : offset+pagination_items]:
                        server_name = individ["server_name"]
                        rep_name = individ["rep"][0]
                        rep_id = individ["rep"][1]
                        manager_name = individ["manager"][0]
                        manager_id = individ["manager"][1]
                        role = individ["verifiedrole"]
                        if role == None:
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
            await interaction.send_message(f"There are no server partners.", ephemeral=True)
            return
        

            


    # VIEW THE SETTINGS
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def showsettings(self, ctx):
        
        """ View the settings for the Overseer Aspect. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        all_embeds = []
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'show_settings' sub-command of 'overseer settings' command.")
            return
        
        # Collect all the booleans
        booster_log_bool = await self.config.guild(guild).enable_booster_log()
        unverified_role_bool = await self.config.guild(guild).enable_unverified_role()
        member_blacklist_bool = await self.config.guild(guild).enable_member_blacklist()
        member_blacklist_auto_action_bool = await self.config.guild(guild).enable_member_blacklist_auto_action()
        server_blacklist_bool = await self.config.guild(guild).enable_server_blacklist()
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
            top_role = get(guild.roles, id=await self.config.guild(guild).top_role())
            top_role = top_role.mention
        except:
            top_role = "Not set."

        try:
            admin_role = await Red.get_admin_roles(ctx.bot, guild)
            admin_role = [role.mention for role in admin_role]
            rolelist = ""
            
            if len(admin_role) == 1:
                rolelist = f"{admin_role[0]}"
            else:
                for mentions in admin_role[:1]:
                    rolelist += f"{mentions}, "
                rolelist += f"{admin_role[len(admin_role)-1]}"
                admin_role = rolelist
        except:
            admin_role = "Not set."

            
        try:
            mod_role = await Red.get_mod_roles(ctx.bot, guild)
            mod_role = [role.mention for role in mod_role]
            rolelist = ""
            if len(mod_role) == 1:
                rolelist = f"{mod_role[0]}"
            else:
                for mentions in mod_role[:1]:
                    rolelist += f"{mentions}, "
                rolelist += f"{mod_role[len(mod_role)-1]}"
            mod_role = rolelist
        except:
            mod_role = "Not set."


        # Collect all the channels
            
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
        bools = f"**Enable Navigation:** {navigation_bool} \n**Enable DM for Staff-Action:** {dm_bool} \n**Enable Booster Log:** {booster_log_bool} \n**Enable Unverified Role:** {unverified_role_bool} \n**Enable Public Moderation:** {public_mod_bool} \n**Enable Quarantine:** {quarantine_bool} \n**Enable Threshold:** {threshold_bool} \n**Enable Member Blacklist:** {member_blacklist_bool} \n**Enable Member Blacklist Auto Action:** {member_blacklist_auto_action_bool} \n**Enable Server Blacklist:** {server_blacklist_bool} \n**Enable Verification:** {verification_bool} \n**Enable Member = ID-Verified:** {member_equal_id_bool} \n**Enable Verify:** {verify_bool} \n**Enable Entry:** {entry_bool} \n**Enable Codeword:** {codeword_bool} \n**Enable Welcome:** {welcome_bool} \n**Enable Introduction:** {introduction_bool} \n**Enable Instruction:** {instructions_bool} \n**Enable Verification Log:** {verification_log_bool} \n**Enable Partner Verification Log:** {partner_verification_bool}"
        bool_embed = discord.Embed(title="**Overseer Settings**", description="# **Enabled / Disabled Settings**:\n" + bools, color=clr)
        bool_embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        bool_embed.add_field(name="Date", value="{}".format(timestamp))
        bool_embed.set_footer(text="Page    2 / 5")
        all_embeds.append(bool_embed)
        
        # Moderation: All settings
        mods = f"# **Miscellaneous:**\n**Threshold Action**: {threshold_action} \n**Warn Threshold**: {warn_threshold} \n**Incident Threshold**: {incident_threshold} \n**Member Blacklist Auto Action:** {member_auto_action} \n\n# **Roles:** \n**Staff Role**: {staff_role} \n**Moderator Role**: {mod_role} \n**Admin Role**: {admin_role} \n**Quarantine Role**: {quarantine_role} \n**Booster Role**: {booster_role} \n**Server Partner**: {serverpartner_role}\n**Top Role (Boosting)**: {top_role} \n\n# **Channels:** \n**Public Moderation Channel**: {public_moderation_channel} \n**Log Channel**: {log_channel} \n**Mod Log Channel**: {modlog_channel} \n**Staff Channel**: {staff_channel} \n**Boost Channel**: {boost_channel} \n**Navigation Channel**: {map_channel} \n**Quarantine Channel**: {quarantine_channel}"
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
        
        verif_2 = f"# **Miscellaneous:** \n**Codeword**: {codeword} \n\n**Welcome Message**: {welcome_message} \n\n**Introduction Message**: {introduction} \n\n**Instruction Message**: {instruction}"
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


    # LOGGING FOR MODERATION

    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def clearuserlogs(self, ctx, user: discord.User, choice: str=None):
        
        """ 
        Clear the moderation logs. \n
        Leaving the second option empty will delete all. \n
        Enter a user first. \n
        Choices: Kicks, bans, incidents, timeouts, warns, quarantines, notes (only for users), or leave choice empty. 
        """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clearlogs' sub-command of 'moderation logging' command.")
            return
        

        userlog = await self.config.guild(guild).users()
        is_in = element_check(self, ctx, userlog, "member_id", user.id)
            
        if is_in[0] == False:
            await ctx.send("This user does not have logs.")
            return
            
        target = is_in[1]
            
            
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
            await ctx.send("You need to enter one of the valid choices.")
            return
        
        userlog[user.id] = target
        await self.config.guild(guild).users.set(userlog)
            
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def clearserverlogs(self, ctx, choice: str=None):
        
        """ 
        Clear the moderation logs. \n
        Leaving the second option empty will delete all. \n
        Choices: Kicks, bans, incidents, timeouts, warns, quarantines, notes (only for users). 
        """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clearlogs' sub-command of 'moderation logging' command.")
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
            await ctx.send("You need to enter a valid choice from kicks, bans, incidents, timeouts, warns, quarantines.")
            return


    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def viewuserlogs(self, ctx, option: discord.User, choice: str):
        
        """ 
        View the moderation logs. \n
        Enter a user. \n
        Choices: Kicks, bans, timeouts, warns, quarantines, threshold. 
        """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'viewlogs' sub command of 'moderation'.")
            return

        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return

        if choice.lower() in ["kicks", "bans", "warns", "quarantines", "timeouts", "threshold"]:
            
            user = option
            member = option
            user_logs = await self.config.guild(guild).users()
            is_in = element_check(self, ctx, user_logs, "member_id", user.id)
            if is_in[0] == False:
                    user_logs[user.id] = {
                        "member_id" : user.id,
                        "member_name" : user.name,
                        "guild" : [guild.name, guild.id],
                        "kicks" : [], # Kick logs
                        "bans" : {}, # Ban logs
                        "quarantines" : {}, # Quarantine logs
                        "timeouts" : [], # Timeout logs
                        "warns" : [], # Warn logs
                        "notes" : [], # User notes
                        "threshold" : 0 # incident count
                    }
                    target = user_logs[user.id]
            else:
                    target = is_in[1]
            
                
            if choice.lower() not in ["kicks", "bans", "warns", "quarantines", "timeouts", "threshold"]:
                await ctx.send(f"My apologies, dear {author.name}, however, I can only accept the names of existing log categories. \nExisting categories are: \n- threshold, \n- kicks, \n- bans, \n- warns,\n- timeouts, \n- quarantines")
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
                    await ctx.send("This user does not have any warns currently.")
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

        else:
            await ctx.send("You need to enter a valid category. \nExisting categories are: \n- threshold, \n- kicks, \n- bans, \n- warns,\n- timeouts, \n- quarantines")
            return
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def viewserverlogs(self, ctx, choice: str=None):
        
        """ 
        View the moderation logs. \n
        Choices: Kicks, bans, incidents, timeouts, warns, quarantines. 
        """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'viewlogs' sub command of 'moderation'.")
            return

        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
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


    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def synchronize(self, ctx):
        """ 
        Synchronise all member logs. \n 
        It adds a log for every server's member, who is not yet logged. 
        """
        
        guild = ctx.guild
        author = ctx.author
        user_logs = await self.config.guild(guild).users()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'synchronize' subcommand of 'moderation ' command.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        tally = 0
        
        for member in guild.members:
            is_in = element_check(self, ctx, user_logs, "member_id", member.id)
            if is_in[0] == False:
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

        await ctx.send(f"I have synchronised the user logs and added {tally} users.")
        await self.config.guild(guild).users.set(user_logs)
    
    
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def deleteuserlog(self, ctx, user: discord.User, number: str, choice: str=None):
        
        """ 
        Delete a specific log entry for option (user or server log) and choice (see below). \n
        Leaving the third option empty will delete all. \n
        Enter a valid user, then a number. \n
        Choices: Kicks, bans, incidents, timeouts, warns, quarantines, notes (only for users). 
        """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'deletelog' sub-command of 'moderation' command.")
            return
        
        if number <= 0:
            await ctx.send("You need to enter a number bigger than zero.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return

        user_logs = await self.config.guild(guild).users()
        is_in = element_check(self, ctx, user_logs, "member_id", user.id)
        if is_in[0] == False:
                user_logs[user.id] = {
                    "member_id" : user.id,
                    "member_name" : user.name,
                    "guild" : [guild.name, guild.id],
                    "kicks" : [], # Kick logs
                    "bans" : {}, # Ban logs
                    "quarantines" : {}, # Quarantine logs
                    "timeouts" : [], # Timeout logs
                    "warns" : [], # Warn logs
                    "notes" : [], # User notes
                    "threshold" : 0 # incident count
                }
        else:
                target = is_in[1]
                
        if choice.lower() not in ["kicks", "bans", "ban", "kick", "quarantines", "quarantine", "timeouts", "timeout", "warns", "warn"]:
                await ctx.send("My apologies, however, you need to enter either kicks, bans, quarantines, timeouts, or warns, or incidents.")
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

        user_logs[user.id] = target
        await self.config.guild(guild).users.set(user_logs)
            
    @moderation.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def deleteserverlog(self, ctx, number: str, choice: str=None):
        
        """ 
        Delete a specific log entry for option (user or server log) and choice (see below). \n
        Leaving the third option empty will delete all. \n
        Choices: Kicks, bans, incidents, timeouts, warns, quarantines, notes (only for users). 
        """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'deletelog' sub-command of 'moderation' command.")
            return
        
        if number <= 0:
            await ctx.send("You need to enter a number bigger than zero.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
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



        
    
    
    
    
    
    


    # LOGGING FOR MODERATION
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def listusers(self, ctx, member: discord.User=None):
        
        """ 
        List all the currently verified users in detail, or a single user. \n
        Leave empty to show all verified users. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'listusers' sub command of 'verification'.")
            return
        
        verifications = await self.config.guild(guild).verified_users()
        
        if verifications == {}:
            await ctx.send("My apologies, however, currently there do not exist any verified users.")
            return
        
        if member != None:
            
            is_in = element_check(self, ctx, verifications, "member_id", member.id)
            if is_in[0] == False:
                if member not in guild.members:
                    await ctx.send("This member is not verified, and not part of the server.")
                    return
                else:
                    await ctx.send("This member is not verified.")
                    return
            else:
                target = is_in[1]

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
                                # Delete the verification if the user is staff
                                if staffrole in author.roles or staff_check(self, ctx, author):
                                    verifications.pop(str(member.id))
                                    await self.config.guild(ctx.guild).verified_users.set(verifications)
                                    await asyncio.sleep(5)
                                    await ctx.send("You have successfully deleted this verification.")
                                    await message.delete()
                                    break
                                else:
                                    await ctx.send("You do not have permission to delete verifications.")
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
                await ctx.send(f"My apologies, there aren't any verified members yet.")
                return
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def isverified(self, ctx, member: discord.User):
        
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
        elif not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        elif verifications == {}:
            await ctx.send("My apologies, however, there are no currently verified users.")
            return
    
        
        is_in = element_check(self, ctx, verifications, "member_id", member.id)
        
        if is_in[0] == False:
            if member not in guild.members:
                await ctx.send("This member is not verified, and not part of the server.")
                return
            else:
                await ctx.send("This member is not verified.")
                return
        else:
            target = is_in[1]
  
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
    
    @verification.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def deletelogs(self, ctx, choice: str=None, user: discord.User=None):
        """ Purge the logs (for cross- or verification). Leaving it empty will delete both. """

        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'deletelogs' sub-command of 'verification' command.")
            return

        if choice == None and user == None:
            await self.config.guild(guild).verified_users.set({})
            await self.config.guild(guild).crossverified_users.set({})
            settings = f"\n **Log Purge:** \n The verification and crossverification logs have been purged."
        
            embed = discord.Embed(title="Overseer Verification: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif user != None and choice == None:
            verif = await self.config.guild(guild).verified_users.set({})
            crossverif = await self.config.guild(guild).crossverified_users.set({})
        
            is_in = False
            if user.id in crossverif:
                    is_in= True
                    target = crossverif[user.id]
                
            if is_in:
                    crossverif.pop(target)
            else:
                    await ctx.send("This member is not crossverified. I could not remove them from the list.")

            is_in = False
            if user.id in verif:
                    is_in= True
                    target = verif[user.id]
                
            if is_in:
                    verif.pop(target)
            else:
                    await ctx.send("This member is not verified. I could not remove them from the list.")
                
            
            await self.config.guild(guild).verified_users.set(verif)
            await self.config.guild(guild).crossverified_users.set(crossverif)    
            
            settings = f"\n **Log Purge:** \n The logs of {user.name} have been purged."
        
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
        elif user != None and choice.lower() in ["crossverified", "crossverification", "crossverifications", "crossverified users", "crossverification logs", "verified", "verification", "verifications", "verified users", "verification logs"]:
            verif = await self.config.guild(guild).verified_users.set({})
            crossverif = await self.config.guild(guild).crossverified_users.set({})
            
            if choice.lower() in ["crossverified", "crossverification", "crossverifications", "crossverified users", "crossverification logs"]:
                
                is_in = False
                if user.id in crossverif:
                    is_in= True
                    target = crossverif[user.id]
                
                if is_in:
                    crossverif.pop(target)
                else:
                    await ctx.send("This member is not crossverified. I could not remove them from the list.")
                
            elif choice.lower() in ["verified", "verification", "verifications", "verified users", "verification logs"]:
                is_in = False
                if user.id in verif:
                    is_in= True
                    target = verif[user.id]
                
                if is_in:
                    verif.pop(target)
                else:
                    await ctx.send("This member is not verified. I could not remove them from the list.")
                
            
            await self.config.guild(guild).verified_users.set(verif)
            await self.config.guild(guild).crossverified_users.set(crossverif)    
            
            settings = f"\n **Log Purge:** \n The {choice.lower()} logs of {user.name} have been purged."
        
            embed = discord.Embed(title="Overseer Verification: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
            
        else:
            await ctx.send("My apologies, you have entered the wrong option. Please either leave it empty, choose 'verification', or 'crossverification', and possibly a user.")
        
    
    
    
    # LOGS: NOTES
    
    @commands.group(name="notes")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def notes(self, ctx):
        
        """ 
        Relating to notes about users. \n
        Similar to flagging. 
        """
    
    @notes.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def addnote(self, ctx, member: discord.User, *, message: str):
        """ Add a note to a user. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        target = None
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Get roles and channels
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'addnote' subcommand of 'notes' command.")
            return
        
        if not (await staff_check(self, ctx, author)):
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
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
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
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        note_log = None
        user_note_log = None
        
        # Get roles and channels

        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        modlog_channel = get(guild.channels, id = await self.config.guild(guild).modlog_channel())

        # Check for cases where user / member are staff. Ensure hierarchy.
        if staffrole== None or modlog_channel == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'remove' subcommand of 'notes' command.")
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
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        
        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'view' sub command of 'notes'.")
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

    # boosting
        
    @boosting.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def viewlist(self, ctx):
        
        """ 
        View the booster list, including their roles. 
        """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        boostlogs = await self.config.guild(guild).boosting_users()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'viewlogs' sub command of 'boosting'.")
            return

        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return


        
        if boostlogs != {}:
            boostlist = list(boostlogs.values())
            all_embeds = []
            pagination_items = 4
                    
            total_items = len(boostlist)
                    
            total_pages_items = total_items // pagination_items+1
            if total_items % pagination_items==0:
                        total_pages_items = total_items // pagination_items
            else:
                        total_pages_items = total_items // pagination_items+1
                    
            for page in range(1, total_pages_items+1):
                        
                # Log embed
                embed = discord.Embed(title="", 
                                                    description=f"# ** Boosting Users**\n\n The Date format is DD/MM/YYYY.\n\n", 
                                                    color=clr)
                embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                        
                offset = (page-1)*pagination_items
                if abs(page*pagination_items - total_items) < pagination_items:
                            
                    for individ in boostlist[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                        member_name = individ["user_name"]
                        member_id = individ["user_id"]
                        custom_role_id = individ["custom_role"]
                        custom_colour = individ["custom_colour"]
                        custom_name = individ["custom_name"]
                        date = individ["date"]
                        crole = get(guild.roles, id = custom_role_id)
                        if crole == None:
                            embed.description += f"User:          {member_name} ({member_id})\nRole:          Missing        \nDetails:        {custom_name} ({custom_colour})\nDate:         {date}\n\n"
                        else:
                            embed.description += f"User:          {member_name} ({member_id})\nRole:          {crole.mention}\nDetails:        {custom_name} ({custom_colour})\nDate:         {date}\n\n"
                else:
                            
                    for individ in boostlist[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                        member_name = individ["user_name"]
                        member_id = individ["user_id"]
                        custom_role_id = individ["custom_role"]
                        custom_colour = individ["custom_colour"]
                        custom_name = individ["custom_name"]
                        date = individ["date"]
                        crole = get(guild.roles, id = custom_role_id)
                        if crole == None:
                            embed.description += f"User:          {member_name} ({member_id})\nRole:          Missing\nDetails:          {custom_name} ({custom_colour})\nDate:            {date}\n\n"
                        else:
                            embed.description += f"User:          {member_name} ({member_id})\nRole:          {crole.mention}\nDetails:          {custom_name} ({custom_colour})\nDate:            {date}\n\n"
                                
                                
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
            await ctx.send("There aren't any boosting members presently.")
            return
    
    @boosting.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def clean(self, ctx, option: discord.User=None):
        
        """ 
        Delete a specific entry (=name a user) or the entire list (= leave it empty).
        """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        boostlogs = await self.config.guild(guild).boosting_users()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'viewlogs' sub command of 'boosting'.")
            return

        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return

        if option == None:
            await ctx.send("This will remove all currently listed boosting users from the log. Are you sure you want to proceed?")
            try:
                async with asyncio.timeout(150):
                    msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
            except TimeoutError:
                await ctx.send("You have taken too long to respond.")
                return
            
            if "yes" in msg.content.lower() or "yes" in msg.content.lower():
                await self.config.guild(guild).boosting_users.set({})
                await ctx.send("You have reset the booster log.")
            else:
                await ctx.send("Cancelling procedure.")
                return
        else:
            
            is_in = False
            target = None
            
            for items in list(boostlogs.values()):
                if items["user_id"] == option.id:
                    is_in = True
                    target = items
            
            if boostlogs == {} or target == None or is_in == False:
                await ctx.send("Unfortunately, this user is not a booster.")
                return
            else:
                boostlogs.pop(str(option.id))
                await ctx.send(f"You removed the log for {option.name}.")
                await self.config.guild(guild).boosting_users.set(boostlogs)

    @boosting.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def hasrole(self, ctx, option: discord.User):
        
        """ 
        Figure out if a user has a boosting role already.
        """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        boostlogs = await self.config.guild(guild).boosting_users()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'viewlogs' sub command of 'boosting'.")
            return

        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return

        is_in = False
        target = None
            
        for items in list(boostlogs.values()):
                if items["user_id"] == option.id:
                    is_in = True
                    target = items
            
        if boostlogs == {} or target == None or is_in == False:
                await ctx.send("Unfortunately, this user is not a booster.")
                return
        else:
            role = get(guild.roles, id = target['custom_role'])
            if role == None:
                await ctx.send("This user does not have a booster role.")
            else:
                await ctx.send(f"User {option.name} has the role {role.name} ({role.id}) with color {target['custom_colour']} and name {target['custom_name']}.")

    @boosting.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def timesup(self, ctx):
        
        """ 
        Show a list of users that do not deserve their boost roles anymore, and take them away if commanded to.
        """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        boostlogs = await self.config.guild(guild).boosting_users()
        boost_role = get(guild.roles,id= await self.config.guild(guild).booster_role())
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'viewlogs' sub command of 'boosting'.")
            return

        if staffrole == None:
            await ctx.send("My apologies, however, you are lacking a setup. Please set the proper channels and roles.")
            return
        
        if not (await staff_check(self, ctx, author)):
            await ctx.send("My apologies, however, you need to be a staff member to use this command.")
            return

        boostlist = list(boostlogs.values())
        
        bad_list = []
        
        for items in boostlist:
            user_id = items['user_id']
            user = await guild.query_members(user_ids=[user_id]) # list of members with userid
            user = user[0]
            user_role = get(guild.roles, id = items['custom_role'])
            
            if user_role == None:
                user_role = "Missing"
            if user == None:
                user = "Missing"
                
            if boost_role not in user.roles or user not in guild.members:
                bad_list.append([user, user_role])
        

        if bad_list:
                all_embeds = []
                pagination_items = 10
                
                total_items = len(bad_list)
                
                total_pages_items = total_items // pagination_items+1
                if total_items % pagination_items==0:
                    total_pages_items = total_items // pagination_items
                else:
                    total_pages_items = total_items // pagination_items+1
                
                for page in range(1, total_pages_items+1):
                    
                    # Log embed
                    embed = discord.Embed(title="", 
                                                description=f"# ** Users that are not boosting anymore**\n\nThe Date format is DD/MM/YYYY.\n\n", 
                                                color=clr)
                    embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
                    
                    offset = (page-1)*pagination_items
                    if abs(page*pagination_items - total_items) < pagination_items:
                        for individ in bad_list[offset : offset+pagination_items-abs(offset+pagination_items - total_items)+1]:
                            user = individ[0]
                            role = individ[1]
                            if user != "Missing":
                                if role != "Missing":
                                    embed.description += f"User Name: {user.mention} ({user.id} | {user.name})\nUser's Role: {role.mention}"
                                else:
                                    embed.description += f"User Name: {user.mention} ({user.id} | {user.name})\nUser's Role: {role.name}"
                            else:
                                if role != "Missing":
                                    embed.description += f"User Name: {user.name} ({user.id})\nUser's Role: {role.mention}"
                                else:
                                    embed.description += f"User Name: {user.name} ({user.id})\nUser's Role: {role.name}"
                    else:
                        for individ in bad_list[offset : offset+pagination_items]:
                            user = individ[0]
                            role = individ[1]
                            if user != "Missing":
                                if role != "Missing":
                                    embed.description += f"User Name: {user.mention} ({user.id} | {user.name})\nUser's Role: {role.mention}"
                                else:
                                    embed.description += f"User Name: {user.mention} ({user.id} | {user.name})\nUser's Role: {role.name}"
                            else:
                                if role != "Missing":
                                    embed.description += f"User Name: {user.name} ({user.id})\nUser's Role: {role.mention}"
                                else:
                                    embed.description += f"User Name: {user.name} ({user.id})\nUser's Role: {role.name}"
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
        
                await ctx.send("Do you want to remove their roles from them?")
                
                try:
                        async with asyncio.timeout(150):
                            msg = await self.bot.wait_for("message", check=lambda message: message.author == author)
                except TimeoutError:
                    await ctx.send("You have taken too long to respond.")
                    return
                        
                if "no" in msg.content.lower():
                        await ctx.send("Then they will not be removed.")
                        return
                        
                elif "yes" in msg.content.lower() or "ye" in msg.content.lower():
                    msgstring = ""
                    for item in bad_list:
                        role = item[1]
                        user = item[0]
                        if role != "Missing" and user != "Missing":
                            await user.remove_roles(role)
                        msgstring += f"I removed {user.mention}'s role {role.mention}. \n"
                    
                    await ctx.send(msgstring)
        
        else:
            await ctx.send(f"It seems as if there aren't any boosters who aren't boosting currently.")
        
