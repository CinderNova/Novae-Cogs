
import discord, json, random, datetime, asyncio
import redbot.core.data_manager
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
from discord import webhook
from .abc import MixinMeta, CompositeMetaClass
from .core.headspace import Headspace
from .core.settings import Settings
from .core.kinkprofile import Kinkprofile
from .core.commands import Commands

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




class kinkify(commands.Cog, Settings, Headspace, Commands, Kinkprofile, metaclass=CompositeMetaClass):
    """
    Manage kink-related commands.
    """
    
    # Set the timestamp as of now.
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    
    __version__ = "v3.0.0"
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/debug.log"
        self.debug_file = None
        self.identifier = self.bot.user.id
        self.config = Config.get_conf(self, identifier = self.identifier, force_registration=True)
        default_guild = {
            "enable_debug" : False,
            
            # A server-side safeword. Default for new user profiles.
            "safeword" : "code red",
            # Collection of user profiles. Default:
            "user_profiles" : {
            },
            
            # Roles required in the setup
            "manager_role" : None, # role that can jail, gag, ....
            "nsfw_role" : None,
            "sfw_role" : None,
            "little_role" : None,
            "level_role" : None, # required for the nsfw role
            "staff_role" : None,
            "jail_role" : None, # jailed role
            "claimed_role" : None, # Assigned when claimed
            "gagged_role" : None, # Assigned when gagged
            "id_role" : None,
            
            
            # Channels required in the setup
            "modlog_channel" : None,
            "log_channel" : None,
            "jail_log_channel" : None,
            "staff_channel" : None,
            "jail_channel" : None,
            "boundaries" : None,
            "claim_channel" : None,
            "task_channel" : None,
            
            
            # roles and members that are immune to the jail AND gag; counts for strikes, bad words, etc. as well
            "immunity" : { 
                "roles": [], 
                "members" : []
            },
            # roles and members immune to being jailed
            "jail_immunity" : { 
                "roles" : [], 
                "members" : []
                }, 
            # roles and members immune to being gagged
            "gag_immunity" : {
                "roles" : [], 
                "members" : []
                },
            
            
            
            # Jail booleans and jail list
            "enable_jail" : False, # enable jail
            "enable_staff_jail_immunity" : True, # staff cannot be jailed
            "enable_ask_jail" : False, # ask to be jailed
            "enable_jail_logging" : False, # enable jail logging

            
            # Gagging and Claim booleans
            "enable_gag" : False,
            "enable_staff_gag_immunity" : True,
            "enable_gag_owned_sub" : False, # Gag an owned sub or not
            "enable_gag_preference" : False, # Set preference for gag command
            "enable_claims" : False,
            "enable_claims_strikes" : False,
            "enable_claims_multiclaim" : False,

            "member_claims" : {},  # Comprehensive list of members' claims
            
            
            
            # Headspace booleans and roles
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
                "none" : None
            },
            
            
            
            # Task system booleans
            "enable_task_system" : False,
            "enable_task_member_suggestion" : False,
            
            # Tasks in the task system. Saves task as string and person if not anonymous:
            # task_example = { "author_id" : ..., "author_name" : ..., "description": "do x!", "anonymous": True / False}
            "tasks" : {
                "task_list" : [],
                "task_collaborators" : {}
            }, 
            
            
            
            
            # Standard Exceptions to being jailed:
            # Dominants, Littles, Staff, Immunity-Roles, Headspace (None, dominant, red), sfw-role
            
        }
        self.config.register_guild(**default_guild)
        default_user_profile = {
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : "muffled",
            "jail_preference" : "nobody",
            "gag_preference" : "nobody",
            "general_preference" : "nobody",
            "roles" : None,
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : "red",
            "claims" : {},
            "color" : "#ffffff"
        }
        self.config.register_user(**default_user_profile)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        
        guild = message.guild
        author = message.author
        message_channel = message.channel
        content = message.content
        
        # Get roles first
        staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
        gagged_role = get(guild.roles, id = await self.config.guild(guild).gagged_role())
        jail_log_channel = get(guild.channels, id= await self.config.guild(guild).jail_log_channel())
        gagged_members_dict = await self.config.guild(guild).gagged_members()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        
        profiles = await self.config.guild(guild).user_profiles()
        user = userprofile(self, author)
        
        for key in profiles:
            if profiles[key]["member_id"] == author.id:
                user = profiles[key]
        
        safeword = user["safeword"]
        gag_type = user["gag_type"]
        
        if author == self.bot:
            return
        
        if gagged_role != None:
            if gagged_role in author.roles:
                Noises = ["mpphf"]
                if gag_type == "muffled":
                    Noises = ['Mmmfff','Mmph','Mm','MMMm','Mmmrph','Mmmgh','mmgph','mmmmm','mm','MmMPhh','MMmgH','MMmmm', "mmMMphff"]
                elif gag_type == "drooling":
                    Noises = ["mmmhh", "fffuck", "goddess", "I'm such a slut", "I'm needy", "pleaseee", "punish me", "mmmnf"]
                elif gag_type == "animal":
                    Noises = ["woof", "grrrr", "grr", "awoo", "wuff", "rrrr", "awooof"]
                else:
                    user["gag_type"] = "muffled"
                    gag_type = "muffled"
                    profiles[author.id] = user
                    await self.config.guild(guild).user_profiles.set(profiles)
                
                if safeword.lower() in content.lower() or "code red" in content.lower():
                    await message_channel.send("Gag has been removed.")
                    await author.remove_roles(gagged_role)
                    gagged_members_dict.pop(str(author.id))
                    
                    await self.config.guild(guild).gagged_members.set(gagged_members_dict)
                    return
                    
                
                wordlist = message.content.split()
                        
                NumOWords = len(wordlist)
                i = 0
                    
                    
                Noise = []
                while i != NumOWords:
                            i += 1
                            Noise.append(random.choice(Noises))
                GagNoises = ' '.join(Noise)
                GagNoises += f" \n-# Original Message: {content}"
                try: 
                    webhook = await message.channel.create_webhook(name="webhook")
                    await webhook.send(GagNoises, username = author.display_name, avatar_url = author.avatar.url)
                        
                except discord.HTTPException:
                    await message_channel.send("failed")
                await message.delete()
                await webhook.delete()


    # JAIL COMMANDS
    
    @app_commands.command(description="Jail a naughty member.")
    @app_commands.guild_only()
    @app_commands.describe(member="Choose the member you wish to jail.", duration="Choose the duration [in whole minutes] to jail someone for - Optional.", reason="Add a reason for why this member is being jailed - Optional.")    
    async def jail(self, interaction: discord.Interaction, member: discord.Member, duration: int=None, reason: str=None):
        
        """ Jail a member using this command. """
        
        guild = interaction.guild
        author = interaction.user
        
        # Get roles first
        staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
        jail_role = get(guild.roles, id= await self.config.guild(guild).jail_role())
        jail_log_channel = get(guild.channels, id= await self.config.guild(guild).jail_log_channel())
        profiles = await self.config.guild(guild).user_profiles()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        user = {
            "member_name" : member.name,
            "member_id" : member.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : None,
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "roles" : None,
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        
        
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
        manager_role=  await self.config.guild(guild).manager_role()
        manager_role = get(guild.roles, id=manager_role)

        # General immunity list
        immune_list = await self.config.guild(guild).immunity()
        immune_members, immune_roles = immune_list["members"], immune_list["roles"]
        immune_members_clean, immune_roles_clean = [get(guild.members, id=member) for member in immune_members if get(guild.members, id=member) != None], [get(guild.roles, id=role) for role in immune_roles if get(guild.roles, id=role) != None]

        # Jail immunity list
        jail_immune_list = await self.config.guild(guild).jail_immunity()
        jail_immune_members, jail_immune_roles = jail_immune_list["members"], jail_immune_list["roles"]
        jail_immune_members_clean, jail_immune_roles_clean = [get(guild.members, id=member) for member in jail_immune_members if get(guild.members, id=member) != None], [get(guild.roles, id=role) for role in jail_immune_roles if get(guild.roles, id=role) != None]
        # Check if the dictionary already contains our member
        
        # Check if the member is a manager
        if manager_role not in author.roles:
            await interaction.response.send_message("Dear, you are not permitted to jail another member, you do not have the qualification.", ephemeral=True)
            return
        
        immunity_checks_jail= await immunity_check(self, interaction, member, True, False)
        if immunity_checks_jail[1] or immunity_checks_jail[0]:
            await interaction.response.send_message("You are not permitted to jail this member, since they are immune.", ephemeral=True)
            return
        
        if await self.config.guild(guild).enable_staff_jail_immunity() == True or await self.config.guild(guild).enable_staff_immunity() == True:
            if staff_role in member.roles:
                await interaction.response.send_message("You are not permitted to jail this member, since they are immune.", ephemeral=True)
                return
        if duration <= 0:
            await interaction.response.send_message("You need to enter a valid amount of time.", ephemeral=True)
            return
        
        
        member_roles_ids = [i.id for i in member.roles if i in member.roles]
        member_roles_stored = member.roles
        
        
        for key in profiles:
                if profiles[key]["member_id"] == member.id:
                    existing = True
                    user = profiles[key]
                      
        if existing == False:
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles.set(profiles)
        already_jailed = user["jail_status"]         
        if reason == None:
            reason = "None"
        
        if jail_role in member.roles or already_jailed == True:
            await interaction.response.send_message(f"Unfortunately, this member is already jailed and hence cannot be jailed again.", ephemeral=True)
            return
        
        
            
        if duration != None:
            
            #Prepare the embeds
            embed = discord.Embed(
                title="Imprisonment", 
                description=f"{author.mention} has jailed {member.mention} for {duration} minute(s) as punishment. \n Reason: {reason}")
            embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            log_jail_embed = discord.Embed(
                title="Log: Imprisonment", 
                description=f"{author.mention} has jailed {member.mention} for {duration} minute(s) as punishment. \n Reason: {reason}")
            log_jail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            log_jail_embed.add_field(
                name= "Roles:", 
                value= f"{[i.mention for i in member.roles if i.mention != None]}", 
                inline=False)
            
            log_unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed after {duration} minute(s).")
            log_unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
            unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed after {duration} minute(s).")
            unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            

            
            # Jail Process
            try:
                await member.edit(roles=[jail_role])
                user["roles"] = member_roles_ids
                await interaction.response.send_message(f"You have jailed {member.mention} for {duration} minute(s), {author.mention}.", ephemeral=True)
                await interaction.channel.send(embed=embed)
                if await self.config.guild(guild).enable_jail_logging():
                    await guild.get_channel(jail_log_channel.id).send(embed=log_jail_embed)
                user["jail_status"] = True
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles(profiles)
            except:
                await interaction.response.send_message(f"You could not jail {member.mention}. There has been an issue with my permissions.", ephemeral=True)
                return
            
            # Wait time + Unjail Process
            modified=duration*60
            await asyncio.sleep(modified)
            
            if jail_role in member.roles:
                try:
                        await member.edit(roles=member_roles_stored)
                        await member.remove_roles(jail_role)

                        await interaction.channel.send(f"{member.mention} has been unjailed. ")
                        await interaction.channel.send(embed=unjail_embed)
                        if await self.config.guild(guild).enable_jail_logging():
                            await guild.get_channel(jail_log_channel.id).send(embed=log_unjail_embed)
                        user["jail_status"] = False
                        profiles["member.id"] = user
                        await self.config.guild(guild).user_profiles(profiles)
                except:
                        await interaction.response.send_message(f"{author.mention}, there has been an issue with my permissions. I could not unjail {member.name}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Unfortunately, this member is not jailed.", ephemeral=True)
                
        else:
            
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
            

            
            # Jail Process
            try:
                await member.edit(roles=[jail_role])
                user["roles"] = member_roles_ids
                await interaction.response.send_message(f"You have jailed {member.mention} for {duration} minute(s), {author.mention}.", ephemeral=True)
                await interaction.channel.send(embed=embed)
                if await self.config.guild(guild).enable_jail_logging():
                    await guild.get_channel(jail_log_channel.id).send(embed=log_jail_embed)
                user["jail_status"] = True
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles(profiles)
            except:
                await interaction.response.send_message(f"You could not jail {member.mention}. There has been an issue with my permissions.", ephemeral=True)
                return


    @app_commands.command(description="Unjail a member.")
    @app_commands.guild_only()
    @app_commands.describe(member="Choose the member you wish to unjail.", reason="Add a reason for why this member is being unjailed - Optional.")    
    async def unjail(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        
        """ This command allows you to unjail someone. """
        
        guild = interaction.guild
        author = interaction.user
        
        # Get roles first
        staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
        jail_role = get(guild.roles, id= await self.config.guild(guild).jail_role())
        jail_log_channel = get(guild.channels, id= await self.config.guild(guild).jail_log_channel())
        profiles = await self.config.guild(guild).user_profiles()

        user = {
            "member_name" : member.name,
            "member_id" : member.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : None,
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "roles" : None,
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }


        # Check if the feature is disabled or enabled and roles are set up
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
        manager_role =  await self.config.guild(guild).manager_role()
        manager_roles = get(guild.roles, id=manager_role)

        
        # Check if the member is a manager
        if manager_roles not in author.roles:
            await interaction.response.send_message("Dear, you are not permitted to unjail another member, you do not have the qualification.", ephemeral=True)
            return
        
        for key in profiles:
                if profiles[key]["member_id"] == member.id:
                    existing = True
                    user = profiles[key]
                      
        if existing == False:
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles.set(profiles)
                
        already_jailed = user["jail_status"]
                 
        if reason == None:
            reason = "None"
        
        if jail_role not in member.roles or already_jailed == False:
            await interaction.response.send_message(f"Unfortunately, this member is already unjailed and hence cannot be unjailed again.", ephemeral=True)
            return
        

        #Prepare the embeds
        unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed.")
        unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
        log_unjail_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been unjailed.")
        log_unjail_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
        # Get roles
        roles_list = user["roles"]
        member_roles_stored = [get(guild.roles, id=role) for role in roles_list if get(guild.roles, id=role) != None]

        try:
                        await member.edit(roles=member_roles_stored)
                        await member.remove_roles(jail_role)
                        user["jail_status"] = False
                        profiles[member.id] = user
                        await self.config.guild(guild).user_profiles(profiles)
                        await interaction.response.send_message(f"{member.mention} has been unjailed. ", ephemeral=True)
                        await interaction.channel.send(embed=unjail_embed)
                        await guild.get_channel(jail_log_channel.id).send(embed=log_unjail_embed)
        except:
                        await interaction.response.send_message(f"{author.mention}, there has been an issue with my permissions. I could not unjail {member.name}.", ephemeral=True)

    
    # Gag command
    
    @app_commands.command(description="Gag a naughty member.")
    @app_commands.guild_only()
    @app_commands.describe(member="Choose the member you wish to gag.", option="Choose out of: [animal, muffled, drooling]",reason="Add a reason for why this member is being gagged - Optional.")    
    async def gag(self, interaction: discord.Interaction, member: discord.Member, option: str=None, reason: str=None):
        
        """ Gag a member using this command. """
        
        guild = interaction.guild
        author = interaction.user
        
        # Get roles first
        staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
        gagged_role = get(guild.roles, id = await self.config.guild(guild).gagged_role())
        jail_log_channel = get(guild.channels, id= await self.config.guild(guild).jail_log_channel())
        gagged_members_dict = await self.config.guild(guild).user_profiles()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        
        
        # Check if the feature is disabled or enabled
        if await self.config.guild(guild).enable_gag() == False:
            await interaction.response.send_message("This feature is currently disabled.",ephemeral=True)
            return  
        elif staff_role == None or gagged_role == None:
            await interaction.response.send_message("This feature is not properly set up. Either the staff or gagged role are missing.",ephemeral=True)
            return
        elif await self.config.guild(guild).enable_jail_logging() and jail_log_channel == None:
            await interaction.response.send_message("While logging is enabled, I was not able to find a log channel for this action. Set the jail log channel.")
            return 
            
        # Get list of manager roles
        manager_roles =  await self.config.guild(guild).manager_role()
        manager_role = get(guild.roles, id=manager_roles)

        # General immunity list
        immune_list = await self.config.guild(guild).immunity()
        immune_members, immune_roles = immune_list["members"], immune_list["roles"]
        immune_members_clean, immune_roles_clean = [get(guild.members, id=member) for member in immune_members if get(guild.members, id=member) != None], [get(guild.roles, id=role) for role in immune_roles if get(guild.roles, id=role) != None]

        # Jail immunity list
        gag_immune_list = await self.config.guild(guild).gag_immunity()
        gag_immune_members, gag_immune_roles = gag_immune_list["members"], gag_immune_list["roles"]
        gag_immune_members_clean, gag_immune_roles_clean = [get(guild.members, id=member) for member in gag_immune_members if get(guild.members, id=member) != None], [get(guild.roles, id=role) for role in gag_immune_roles if get(guild.roles, id=role) != None]

        # Check if the member is a manager
        if manager_role not in author.roles:
            await interaction.response.send_message("Dear, you are not permitted to gag another member, you do not have the qualification.", ephemeral=True)
            return
        

        immunity_checks_gag= await immunity_check(self, interaction, member, False, True)
        if immunity_checks_gag[2] or immunity_checks_gag[0]:
            await interaction.response.send_message("You are not permitted to jail this member, since they are immune.", ephemeral=True)
            return
        
        
        
        
        if await self.config.guild(guild).enable_staff_gag_immunity() == True or await self.config.guild(guild).enable_staff_immunity() == True:
            if staff_role in member.roles:
                await interaction.response.send_message("You are not permitted to gag this member, since they are immune.", ephemeral=True)
                return
        
        
        profiles = await self.config.guild(guild).user_profiles()
        existing = False
        user = {
            "member_name" : member.name,
            "member_id" : member.id,
            "jail_status" : False,
            "gag_status" : False,
            "gag_type" : option,
            "jail_preference" : "everyone",
            "gag_preference" : "everyone",
            "general_preference" : "everyone",
            "roles" : None,
            "bad_words" : [],
            "strikes" : 0,
            "safeword" : await self.config.guild(guild).safeword(),
            "claims" : {},
            "color" : "#ffffff"
        }
        
        if option == None:
            option = "muffled"
        
        
        if option.lower() in ["muffled", "animal", "drooling"]:
            option = option.lower()
        else:
            await interaction.response.send_message(f"You need to enter a valid gag type. Either 'muffled', 'drooling', or 'animal'.")
        for key in profiles:
                if profiles[key]["member_id"] == member.id:
                    existing = True
                    user = profiles[key]
                      
        if existing == False:
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles.set(profiles)
                 
        if reason == None:
            reason = "None"
        already_gagged = user["gag_status"]
        
        if already_gagged == False:
            
            #Prepare the embeds
            embed = discord.Embed(
                title="Gagging", 
                description=f"{author.mention} has gagged {member.mention} as punishment. \n Reason: {reason}")
            embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
        
            log_gag_embed = discord.Embed(
                title="Log: Gagging", 
                description=f"{author.mention} has gagged {member.mention} as punishment. \n Reason: {reason}")
            log_gag_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
            log_ungag_embed = discord.Embed(
                title="Freed from Imprisonment", 
                description=f"{member.mention} has been ungagged.")
            log_ungag_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            ungag_embed = discord.Embed(
                title="Freed from Gagging", 
                description=f"{member.mention} has been ungagged.")
            ungag_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            # Gag Process
            try:
                await member.add_roles(gagged_role)
                await interaction.response.send_message(f"You have gagged {member.mention} with the {option} gag, {author.mention}.", ephemeral=True)
                await interaction.channel.send(embed=embed)
                if await self.config.guild(guild).enable_jail_logging():
                    await guild.get_channel(jail_log_channel.id).send(embed=log_gag_embed)
                user["gag_status"] = True
                user["gag_type"] = option
                profiles[member.id] = user
                await self.config.guild(guild).user_profiles.set(profiles)
            except:
                await interaction.response.send_message(f"You could not gag {member.mention}. There has been an issue with my permissions.", ephemeral=True)
                return
            
            
        elif already_gagged == True:
            
            log_ungag_embed = discord.Embed(
                title="Freed from Gagging", 
                description=f"{member.mention} has been ungagged.")
            log_ungag_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            ungag_embed = discord.Embed(
                title="Freed from Gagging", 
                description=f"{member.mention} has been ungagged.")
            ungag_embed.set_author(
                name=author.name, 
                icon_url = author.display_avatar.url)
            
            
            
            try:
                        await member.remove_roles(gagged_role)
                        await interaction.response.send_message(f"{member.mention} has been ungagged. ", ephemeral=True)
                        await interaction.channel.send(embed=ungag_embed)
                        if await self.config.guild(guild).enable_jail_logging():
                            await guild.get_channel(jail_log_channel.id).send(embed=log_ungag_embed)
                        user["gag_status"] = False
                        profiles[member.id] = user
                        await self.config.guild(guild).user_profiles.set(profiles)
            except:
                        await interaction.channel.send_message(f"{author.mention}, there has been an issue with my permissions. I could not ungag {member.name}.", ephemeral=True)
