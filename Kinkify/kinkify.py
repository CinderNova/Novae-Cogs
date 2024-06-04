
import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager

timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

class kinkify(commands.Cog):
    """
    Manage kink-related commands.
    """
    # Set the timestamp as of now.
    
    
    # Standard Claims:
    # Claim: choose between dom-sub, switch-switch
    
    domsub_claim = {
        "dominant" : None,
        "submissive" : None,
        "rules" : None,
        "strikes" : 0,
        "fully_owned" : True, # let's them be jailed by others or not
        "date_of_claim" : None,
    }
    
    switchswitch_claim = {
        # Two switches, so we just number both subjects
        "first_subject" : None,
        "second_subject" : None,
        
        # fts = first to second, stf = second to first
        "fts_rules" : None,
        "stf_rules" : None,
        
        "fts_strikes" : 0,
        "stf_strikes" : 0,
        
        "first_subject_fully_owned" : True, # let's them be jailed by others or not
        "second_subject_fully_owned" : True,
        
        "date_of_claim" : None,
    }
    
    # User: 
    # Options for Pref: Everyone / Ask for consent
    user_template = {
        "member_name" : None,
        "member_id" : None,
        "member_claims" : {},
        "member_pref_jail" : "everyone",
        "member_pref_gag" : "everyone"
    }
    
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/debug.log"
        self.debug_file = None
        self.identifier = self.bot.user.id
        self.config = Config.get_conf(self, identifier = self.identifier, force_registration=True)
        default_guild = {
            "enable_debug" : False,
            "manager_roles" : { # Can jail, give tasks, gag (except owners)
                "roles" : [], 
                "members" : []
            }, 
            "safeword" : None,
            
            "nsfw_role" : None,
            "sfw_role" : None,
            "little_role" : None,
            
            "staff_role" : None,
            "admin_role" : None,
            "mod_role" : None,
            
            "modlog_channel" : None,
            "log_channel" : None,
            "jail_log_channel" : None,
            "staff_channel" : None,
            
            "enable_staff_immunity" : True, # staff is immune to jail AND gag
            "immunity" : { # roles and members that are immune to the jail AND gag
                "roles": [], 
                "members" : []
            },
            
            
            # Jail
            "enable_jail" : False, # enable jail
            "enable_staff_jail_immunity" : True, # staff cannot be jailed
            "enable_ask_jail" : False, # ask to be jailed
            "enable_jail_logging" : False, # enable jail logging
            "jailed_members" : {}, # whoever is currently in jail
            "jail_role" : None, # jail role
            "jail_immunity" : { # whichever role AND / OR member -cannot- be jailed
                "roles" : [], 
                "members" : []
                }, 
            
            # Gagging and Claim
            "enable_gag" : False,
            "enable_staff_gag_immunity" : True,
            "enable_gag_owned_sub" : False, # Gag an owned sub or not
            "enable_gag_preference" : False, # Set preference for gag command
            "enable_claims" : False,
            "enable_claims_strikes" : False,
            "enable_claims_multiclaim" : False,
            
            "gagged_members" : {}, # Add feature that people can set their own preference (everyone is added to the gagged list but only set to true or false when they're gagged or not)
            "member_claims" : {}, 
            
            "claimed_role" : None, # Assigned when claimed
            "gagged_role" : None, # Assigned when gagged
            "claim_channel" : None,
            "gag_immunity" : {
                "roles" : [], 
                "members" : []
                }, # whichever role AND / OR member -cannot- be gagged
            
            # Headspace
            "enable_headspace" : False,
            "enable_headspace_colour" : False,
            "enable_headspace_bdsm" : False,
            "enable_headspace_logging" : False,
            "headspace_roles_colour" : {
                "red" : None, 
                "yellow" : None,
                "green" : None
                },
            "headspace_roles_bdsm" : {
                "dominant" : None,
                "switch" : None,
                "submissive" : None,
                "None" : None
            },
            
            # Tasks
            "enable_task_system" : False,
            "enable_task_member_suggestion" : False,
            "tasks" : {} # Add task along with person. save as nicknamed task. e.g. "dancing" : {"desc" : "dance!", "author" : "", ...}
            
            # Standard Exceptions to being jailed:
            # Dominants, Littles, Staff, Immunity-Roles, Headspace (None, dominant, red), sfw-role
            
            
        }
        self.config.register_guild(**default_guild)
        
        
        
        
    @commands.group(name="kinkify")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def kinkify(self, ctx):
        """ The group of commands related to managing the kinkify cog. """
    
    
    @kinkify.group(name="settings")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        """ The group of commands related to managing the kinkify -settings-. """
    
    
    @settings.group(name="enable")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx):
        """ The group of commands related to managing the 'enable feature' -settings-. """

    
    @settings.group(name="claiming")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def claiming(self, ctx):
        """ The group of commands related to managing the claiming -settings-. """
    
    
    @settings.group(name="jailing")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def jailing(self, ctx):
        """ The group of commands related to managing the jail -settings-. """
    
    
    
    
    
    
    # Enable - Disable features
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_jail(self, ctx, bools: str):
        """ Enable or disable the jail. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_jail' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_jail.set(True)
            await ctx.send("You have successfully enabled the jail.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_jail.set(False)
            await ctx.send("You have successfully disabled the jail.")
        else:
            await ctx.send("Enter either true or false.")
        
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_staff_jail_immunity(self, ctx, bools: str):
        """ Enable or disable whether or not staff can be jailed. \n If disabled, staff cannot be jailed at all. \n If enabled, Staff will be asked whether they consent or not. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_staff_jail' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_staff_jail.set(True)
            await ctx.send("You have successfully enabled that staff can be jailed.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_staff_jail.set(False)
            await ctx.send("You have successfully disabled that staff can be jailed.")
        else:
            await ctx.send("Enter either true or false.")

    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_ask_jail(self, ctx, bools: str):
        """ Enable or disable whether or not someone can be jailed or has to consent. \n If disabled, they can be jailed without asking. \n If enabled, they have to consent before being jailed. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_ask_jail' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_ask_jail.set(True)
            await ctx.send("You have successfully enabled that everyone can be jailed only with consent.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_ask_jail.set(False)
            await ctx.send("You have successfully disabled that members can be jailed regardless.")
        else:
            await ctx.send("Enter either true or false.")
    
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_gag(self, ctx, bools: str):
        """ Enable or disable the Gag feature. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_gag' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_gag.set(True)
            await ctx.send("You have successfully enabled the Gag feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_gag.set(False)
            await ctx.send("You have successfully disabled the Gag feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_gag_owned_sub(self, ctx, bools: str):
        """ Enable or disable the Gag feature. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_gag_owned_sub' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_gag_owned_sub.set(True)
            await ctx.send("You have successfully enabled that owned submissives can be gagged by anyone.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_gag_owned_sub.set(False)
            await ctx.send("You have successfully disabled that owned submissives can be gagged by anyone.")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_gag_preference(self, ctx, bools: str):
        """ Enable or disable the Gag feature. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_gag_preference' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_gag_preference.set(True)
            await ctx.send("You have successfully enabled member preference for the Gag feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_gag_preference.set(False)
            await ctx.send("You have successfully disabled member mpreference for the Gag feature.")
        else:
            await ctx.send("Enter either true or false.")
    

    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_claims(self, ctx, bools: str):
        """ Enable or disable the Claiming feature. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_claims' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_claims.set(True)
            await ctx.send("You have successfully enabled the Claiming feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_claims.set(False)
            await ctx.send("You have successfully disabled the Claiming feature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_claims_strikes(self, ctx, bools: str):
        """ Enable or disable the Strike feature for Claiming. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_claims_strikes' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_claims_strikes.set(True)
            await ctx.send("You have successfully enabled the Strike feature for Claiming.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_claims_strikes.set(False)
            await ctx.send("You have successfully disabled the Strike feature for Claiming. .")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_claims_multiclaim(self, ctx, bools: str):
        """ Enable or disable multiple claims for Claiming. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_claims_multiclaim' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_claims_multiclaim.set(True)
            await ctx.send("You have successfully enabled the Multiclaim feature for Claiming.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_claims_multiclaim.set(False)
            await ctx.send("You have successfully disabled the Multiclaim feature for Claiming. .")
        else:
            await ctx.send("Enter either true or false.")
    
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_headspace(self, ctx, bools: str):
        """ Enable or disable Headspace. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_headspace' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_headspace.set(True)
            await ctx.send("You have successfully enabled the Headspace feature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_headspace.set(False)
            await ctx.send("You have successfully disabled the Headspace feature.")
        else:
            await ctx.send("Enter either true or false.")
            
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_headspace_colour(self, ctx, bools: str):
        """ Enable or disable Coloured Headspace. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_headspace_colour' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_headspace_colour.set(True)
            await ctx.send("You have successfully enabled the Coloured Headspace subfeature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_headspace_colour.set(False)
            await ctx.send("You have successfully disabled the Coloured Headspace subfeature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_headspace_bdsm(self, ctx, bools: str):
        """ Enable or disable BDSM Headspace. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_headspace_bdsm' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_headspace_bdsm.set(True)
            await ctx.send("You have successfully enabled the BDSM Headspace subfeature.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_headspace_bdsm.set(False)
            await ctx.send("You have successfully disabled the BDSM Headspace subfeature.")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_headspace_logging(self, ctx, bools: str):
        """ Enable or disable Headspace logging. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_headspace_logging' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_headspace_logging.set(True)
            await ctx.send("You have successfully enabled Headspace logging.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_headspace_logging.set(False)
            await ctx.send("You have successfully disabled Headspace logging.")
        else:
            await ctx.send("Enter either true or false.")
    
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_task_system(self, ctx, bools: str):
        """ Enable or disable the task system. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_task_system' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_task_system.set(True)
            await ctx.send("You have successfully enabled the Task System.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_task_system.set(False)
            await ctx.send("You have successfully disabled the Task System.")
        else:
            await ctx.send("Enter either true or false.")
    
    @enable.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def enable_task_member_suggestion(self, ctx, bools: str):
        """ Enable or disable member suggestions for the task system. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_task_member_suggestion' sub-command of 'enable' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bools in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_task_member_suggestion.set(True)
            await ctx.send("You have successfully enabled member suggestions for the Task System.")
        elif bools in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_task_member_suggestion.set(False)
            await ctx.send("You have successfully disabled member suggestions for the Task System.")
        else:
            await ctx.send("Enter either true or false.")
    
    
    
    # Main commands
    
    @app_commands.command(description="Jail a naughty member.")
    @app_commands.guild_only()
    @app_commands.describe(member="Choose the member you wish to jail.", duration="Choose the duration [in whole minutes] to jail someone for - Optional.", reason="Add a reason for why this member is being jailed - Optional.")    
    async def jail(self, interaction: discord.Interaction, member: discord.Member, duration: int=None, reason: str=None):
        
        """ This command allows you to jail someone. """
        
        guild = interaction.guild
        author = interaction.user
        clr = await interaction.embed_colour()

        # Get roles first
        staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
        jail_role = get(guild.roles, id= await self.config.guild(guild).jail_role())
        jail_log_channel = get(guild.channels, id= await self.config.guild(guild).jail_log_channel())
        jailed_members_dict = await self.config.guild(guild).jailed_members()

        
        
        # Check if the feature is disabled or enabled
        if await self.config.guild(guild).enable_jail() == False:
            await interaction.response.send_message("This feature is currently disabled.",ephemeral=True)
            return  
        elif staff_role == None or jail_role == None:
            await interaction.response.send_message("This feature is not properly set up. Either the staff or jail role are missing.",ephemeral=True)
            return
        elif await self.config.guild(guild).enable_jail_logging() and jail_log_channel == None:
            await interaction.response.send_message("While logging is enabled, I was not able to find a log channel.")
            return 
            
        # Get list of manager roles
        manager_roles_raw =  await self.config.guild(guild).manager_roles()
        manager_roles = [get(guild.roles, id=role) for role in manager_roles_raw if get(guild.roles, id=role) != None]

        # General immunity list
        immune_list = await self.config.guild(guild).immunity()
        immune_members, immune_roles = immune_list["members"], immune_list["roles"]
        immune_members_clean, immune_roles_clean = [get(guild.members, id=member) for member in immune_members if get(guild.members, id=member) != None], [get(guild.roles, id=role) for role in immune_roles if get(guild.roles, id=role) != None]

        # Jail immunity list
        jail_immune_list = await self.config.guild(guild).jail_immunity()
        jail_immune_members, jail_immune_roles = jail_immune_list["members"], jail_immune_list["roles"]
        jail_immune_members_clean, jail_immune_roles_clean = [get(guild.members, id=member) for member in jail_immune_members if get(guild.members, id=member) != None], [get(guild.roles, id=role) for role in jail_immune_roles if get(guild.roles, id=role) != None]

        # Check if the member is a manager
        if [manager for manager in manager_roles if manager in author.roles] == []:
            await interaction.response.send_message("Dear, you are not permitted to jail another member, you do not have the qualification.", ephemeral=True)
            return
        elif [role for role in immune_roles_clean if role in member.roles] == [] or [memb for memb in immune_members_clean if member == memb] == [] or [role for role in jail_immune_roles_clean if role in member.roles] == [] or [memb for memb in jail_immune_members_clean if member == memb] == []:
            await interaction.response.send_message("You are not permitted to jail this member, since they are immune.", ephemeral=True)
            return
        elif await self.config.guild(guild).enable_staff_jail_immunity() == True or await self.config.guild(guild).enable_staff_immunity() == True:
            if staff_role in member.roles:
                await interaction.response.send_message("You are not permitted to jail this member, since they are immune.", ephemeral=True)
                return
        elif duration <= 0:
            await interaction.response.send_message("Dear, you need to enter a valid amount of time. Try again.", ephemeral=True)
            return
        
        # Check if the dictionary already contains our member
        target_member_test = None
        for key in jailed_members_dict:
            if jailed_members_dict != {}:
                if jailed_members_dict[key]["member_id"] == member.id:
                    target_member_test = jailed_members_dict[key]
        if target_member_test != None:
            if target_member_test["active"] == True:
                await interaction.response.send_message(f"Unfortunately, this member is already jailed and hence cannot be jailed again.", ephemeral=True)
                return
        
        if reason == None:
            reason = "None"
            
        if duration != None:
            
            
            # Prepare the member roles
            member_roles_ids = [i.id for i in member.roles if i in member.roles]
            member_roles_stored = member.roles
            
            #Prepare the embeds
            embed = discord.Embed(
                title="Imprisonment", 
                description=f"{author.mention} has jailed {member.mention} for {duration} minute(s) as punishment. \n Reason: {reason}", 
                color=clr)
            embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            log_jail_embed = discord.Embed(
                title="Log: Imprisonment", 
                description=f"{author.mention} has jailed {member.mention} for {duration} minute(s) as punishment. \n Reason: {reason}", 
                color=clr)
            log_jail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            log_jail_embed.add_field(
                name= "Roles:", 
                value= f"{[i.mention for i in member.roles if i.mention != None]}", 
                inline=False)
            
            log_unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed after {duration} minute(s).", 
                color=clr)
            log_unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
            unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed after {duration} minute(s).", 
                color=clr)
            unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
            # Prepare the template to save info
            jail_template = {
            "member_id" : member.id,
            "member_name" : member.name,
            "date" : timestamp,
            "roles" : member_roles_ids, 
            "reason" : reason,
            "duration" : duration,
            "active" : True
            }
            
            # Jail Process
            try:
                await member.edit(roles=[jail_role])
                jailed_members_dict[member.id] = jail_template
                await self.config.guild(guild).jailed_members.set(jailed_members_dict)
                await interaction.channel.send(f"You have jailed {member.mention} for {duration} minute(s), {author.mention}.")
                await interaction.channel.send(embed=embed)
                if await self.config.guild(guild).enable_jail_logging():
                    await guild.get_channel(jail_log_channel.id).send(embed=log_jail_embed)
            except:
                await interaction.response.send_message(f"You could not jail {member.mention}. There has been an issue with my permissions.", ephemeral=True)
                return
            
            # Wait time + Unjail Process
            modified=duration*60
            await asyncio.sleep(modified)
            
            target_member_temp = None
            for key in jailed_members_dict:
                if jailed_members_dict != {}:
                    if jailed_members_dict[key]["member_id"] == member.id:
                        target_member_temp = jailed_members_dict[key]
            if target_member_temp != None:
                if target_member_temp["active"] == True:
                    try:
                        await member.edit(roles=member_roles_stored)
                        await member.remove_roles(jail_role)
                        target_member_temp["active"] = False
                        jailed_members_dict[member.id] = target_member_temp
                        await self.config.guild(guild).jailed_members.set(jailed_members_dict)
                        await interaction.channel.send(f"{member.mention} has been unjailed. ", ephemeral=True)
                        await interaction.channel.send(embed=unjail_embed)
                        if await self.config.guild(guild).enable_jail_logging():
                            await guild.get_channel(jail_log_channel.id).send(embed=log_unjail_embed)
                    except:
                        await interaction.channel.send(f"{author.mention}, there has been an issue with my permissions. I could not unjail {member.name}.", ephemeral=True)
            else:
                await interaction.channel.send(f"Unfortunately, {author.mention}, I could not find {member.name} in the logs, and thus they cannot be unjailed by me.")
        else:
            # Prepare the member roles
            member_roles_ids = [i.id for i in member.roles if i in member.roles]
            member_roles_stored = member.roles
            
            #Prepare the embeds
            embed = discord.Embed(
                title="Imprisonment", 
                description=f"{author.mention} has jailed {member.mention} as punishment. \n Reason: {reason}", 
                color=clr)
            embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            log_jail_embed = discord.Embed(
                title="Log: Imprisonment", 
                description=f"{author.mention} has jailed {member.mention} as punishment. \n Reason: {reason}", 
                color=clr)
            log_jail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            log_jail_embed.add_field(
                name= "Roles:", 
                value= f"{[i.mention for i in member.roles if i.mention != None]}", 
                inline=False)
            
            # Prepare the template to save info
            jail_template = {
            "member_id" : member.id,
            "member_name" : member.name,
            "date" : timestamp,
            "roles" : member_roles_ids, 
            "reason" : reason,
            "duration" : "Duration has not been given.",
            "active" : True
            }
            
            # Jail Process
            try:
                await member.edit(roles=[jail_role])
                jailed_members_dict[member.id] = jail_template
                await self.config.guild(guild).jailed_members.set(jailed_members_dict)
                await interaction.channel.send(f"You have jailed {member.mention}, {author.mention}.")
                await interaction.channel.send(embed=embed)
                if await self.config.guild(guild).enable_jail_logging():
                    await guild.get_channel(jail_log_channel.id).send(embed=log_jail_embed)
            except:
                await interaction.response.send_message(f"You could not jail {member.mention}. There has been an issue with my permissions.", ephemeral=True)
                return


    @app_commands.command(description="Unjail a member.")
    @app_commands.guild_only()
    @app_commands.describe(member="Choose the member you wish to unjail.", reason="Add a reason for why this member is being unjailed - Optional.")    
    async def unjail(self, interaction: discord.Interaction, member: discord.Member, duration: int=None, reason: str=None):
        
        """ This command allows you to unjail someone. """
        
        guild = interaction.guild
        author = interaction.user
        clr = await interaction.embed_colour()

        # Get roles first
        staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
        jail_role = get(guild.roles, id= await self.config.guild(guild).jail_role())
        jail_log_channel = get(guild.channels, id= await self.config.guild(guild).jail_log_channel())
        jailed_members_dict = await self.config.guild(guild).jailed_members()


        # Check if the feature is disabled or enabled
        if await self.config.guild(guild).enable_jail() == False:
            await interaction.response.send_message("This feature is currently disabled.",ephemeral=True)
            return  
        elif staff_role == None or jail_role == None:
            await interaction.response.send_message("This feature is not properly set up. Either the staff or jail role are missing.",ephemeral=True)
            return
        elif await self.config.guild(guild).enable_jail_logging() and jail_log_channel == None:
            await interaction.response.send_message("While logging is enabled, I was not able to find a log channel.")
            return 
            
        # Get list of manager roles
        manager_roles_raw =  await self.config.guild(guild).manager_roles()
        manager_roles = [get(guild.roles, id=role) for role in manager_roles_raw if get(guild.roles, id=role) != None]

        
        # Check if the member is a manager
        if [manager for manager in manager_roles if manager in author.roles] == []:
            await interaction.response.send_message("Dear, you are not permitted to unjail another member, you do not have the qualification.", ephemeral=True)
            return
        
        # Check if the dictionary already contains our member
        target_member_test = None
        for key in jailed_members_dict:
            if jailed_members_dict != {}:
                if jailed_members_dict[key]["member_id"] == member.id:
                    target_member_test = jailed_members_dict[key]
        if target_member_test != None:
            if target_member_test["active"] == False:
                await interaction.response.send_message(f"Unfortunately, this member is already unjailed and hence cannot be unjailed.", ephemeral=True)
                return
        
        if reason == None:
            reason = "None"
            
        if duration != None:
            
            #Prepare the embeds
            unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed after {duration} minute(s).", 
                color=clr)
            unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            log_unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed after {duration} minute(s).", 
                color=clr)
            log_unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
            # Get roles
            roles_list = target_member_test["roles"]
            member_roles_stored = [get(guild.roles, id=role) for role in roles_list if get(guild.roles, id=role) != None]

            
            target_member_temp = None
            for key in jailed_members_dict:
                if jailed_members_dict != {}:
                    if jailed_members_dict[key]["member_id"] == member.id:
                        target_member_temp = jailed_members_dict[key]
            if target_member_temp != None:
                if target_member_temp["active"] == True:
                    try:
                        await member.edit(roles=member_roles_stored)
                        await member.remove_roles(jail_role)
                        target_member_temp["active"] = False
                        jailed_members_dict[member.id] = target_member_temp
                        await self.config.guild(guild).jailed_members.set(jailed_members_dict)
                        await interaction.channel.send(f"{member.mention} has been unjailed. ", ephemeral=True)
                        await interaction.channel.send(embed=unjail_embed)
                        await guild.get_channel(jail_log_channel.id).send(embed=log_unjail_embed)
                    except:
                        await interaction.channel.send(f"{author.mention}, there has been an issue with my permissions. I could not unjail {member.name}.", ephemeral=True)
            else:
                await interaction.channel.send(f"Unfortunately, {author.mention}, I could not find {member.name} in the logs, and thus they cannot be unjailed by me.")
    
    