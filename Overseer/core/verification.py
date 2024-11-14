import discord, json, random, asyncio, logging, traceback, redbot.core.data_manager, datetime, re
from redbot.core import commands, app_commands, utils
from redbot.core.bot import Red
from redbot.core.config import Config
from datetime import timedelta
from discord.utils import get

from ..abc import MixinMeta, CompositeMetaClass
from .settings import Settings

class Verification(MixinMeta):
    
    """
    Verification Commands / Methods.
    """
    
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
        clr = 0x4e1f7c
        
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
        elif staffrole == None or memberrole == None or modlog == None or log == None or crossverifiedrole == None:
            await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the staff / member / crossverified role or log / modlog channel.", ephemeral=True)
            return
        elif await self.config.guild(guild).enable_unverified_role():
            if unverifiedrole == None:
                await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set an unverified role.", ephemeral=True)
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
                    if self.config.guild(guild).enable_unverified_role():
                        await member.remove_roles(unverifiedrole)
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). I have given them the member and ID role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). I have given them the member and ID role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
            else:
                if memberrole in member.roles:
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). \n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). \n Method: {memberdict['verification_method']}.", ephemeral=True)
                else:
                    await member.add_roles(memberrole)
                    if self.config.guild(guild).enable_unverified_role():
                        await member.remove_roles(unverifiedrole)
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
           
        elif is_verified == False and crossverified == None:
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
                if self.config.guild(guild).enable_unverified_role() and unverifiedrole != None:
                    await member.remove_roles(unverifiedrole)
            else:
                await member.add_roles(memberrole)
                if self.config.guild(guild).enable_unverified_role() and unverifiedrole != None:
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
                if self.config.guild(guild).enable_unverified_role() and unverifiedrole != None:
                        await member.remove_roles(unverifiedrole)
            else:
                await member.add_roles(memberrole)
                await member.add_roles(crossverifiedrole)
                if self.config.guild(guild).enable_unverified_role() and unverifiedrole != None:
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

    @app_commands.command(description="Give a user the member role.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="Choose a member to give the role to.", birth_date="Enter the birthdate of the user in 'MONTH DD YYYY'. Optional.", comment="Optional comment.")
    async def member(self, interaction: discord.Interaction, member: discord.Member, birth_date: str=None, comment: str=None):
        
        """ Give a user the member role. """
        
        # Basic I/O.
        guild = interaction.guild
        author = interaction.user
        clr = 0x4e1f7c
        
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        memberrole = get(guild.roles, id = await self.config.guild(guild).member_role())
        unverifiedrole = get(guild.roles, id = await self.config.guild(guild).unverified_role())
        id_role = get(guild.roles, id = await self.config.guild(guild).verification_role())
        
        
        modlog = get(guild.channels, id = await self.config.guild(guild).modlog_channel())
        verificationlog = get(guild.channels, id = await self.config.guild(guild).verification_log_channel())
        welcome = get(guild.channels, id = await self.config.guild(guild).welcome_channel())

        log = get(guild.channels, id = await self.config.guild(guild).log_channel())
        
        
        welcome_message = await self.config.guild(guild).welcome_message()
        verifications = await self.config.guild(guild).verified_users()
        crossverifications = await self.config.guild(guild).crossverified_users()
        
        if not await self.config.guild(guild).enable_verification():
            await interaction.response.send_message("My apologies, however, this feature is disabled. You are required to enable it, before commencing.", ephemeral=True)
            return
        elif staffrole == None or id_role == None or memberrole == None or modlog == None or log == None:
            await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set the staff / member / crossverified role or log / modlog channel.", ephemeral=True)
            return
        elif await self.config.guild(guild).enable_unverified_role():
            if unverifiedrole == None:
                await interaction.response.send_message("My apologies, however, you are lacking a setup. Please set an unverified role.", ephemeral=True)
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
                    if self.config.guild(guild).enable_unverified_role():
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
                    if self.config.guild(guild).enable_unverified_role():
                        await member.remove_roles(unverifiedrole)
                    if mod != None:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {mod.name} ({mod.id}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"{member.name} ({member.id}) has already been verified by {memberdict['staff_name']} ({memberdict['staff_id']}). I have given them the member role.\n Method: {memberdict['verification_method']}.", ephemeral=True)
           
        elif is_verified == False:
            await interaction.response.send_message(f"Your wish is my command, dear {author.name}. Proceeding with the verification...", ephemeral=True)
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
            log_title = "**Procedure**"
            log_desc = f"{member.name} has been allowed in our server."

            log_embed = discord.Embed(title= log_title, description = log_desc,color=clr)
            log_embed.add_field(name=f"**Member**", value=f"{member.mention} ({member.name})", inline=False)
            log_embed.add_field(name=f"**Member ID**", value=f"```{member.id}```", inline=True)
            log_embed.add_field(name=f"**Member Birth Date**", value=f"{birth_date}", inline=True)
            log_embed.add_field(name=f"**Staff Member**", value=f"{author.mention} ({author.name}, ```{author.id}```)", inline=False)
            log_embed.add_field(name=f"**Verification Method**", value="Not ID verified", inline=False)
            log_embed.add_field(name=f"**Comments**", value=f"{cmt}", inline=False)
            log_embed.set_footer(text=f"Date: {ts}")
            
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
                "verification_method": "not ID verified",
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
                if self.config.guild(guild).enable_unverified_role() and unverifiedrole != None:
                    await member.remove_roles(unverifiedrole)
            else:
                await member.add_roles(memberrole)
                if self.config.guild(guild).enable_unverified_role() and unverifiedrole != None:
                    await member.remove_roles(unverifiedrole)
            
            
            # Embed : Welcome
            if welcome_message != None and welcome != None and await self.config.guild(guild).enable_welcome():
                str_welcome = f"{member.name} ({member.mention}) has just entered.\n" + welcome_message
                welcome_embed = discord.Embed(title="**Welcome to this new soul!**", 
                                            description=str_welcome, 
                                            color=clr)

                await guild.get_channel(welcome.id).send(embed = welcome_embed)
                
            # Embed : Ticket
            str_ticket = f"Welcome, {member.name}. As you have just finished getting ready, you will be allowed to step into the realm of {guild.name}. For more information, consider looking around."
            ticket_embed =discord.Embed(title=f"**Welcome to {guild.name}!**", description=str_ticket, color=clr)
            await interaction.channel.send(embed=ticket_embed)

            
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
            
            if await self.config.guild(guild).enable_entry() == False:
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

            if await self.config.guild(guild).enable_entry() == False:
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
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        
        instructions = await self.config.guild(guild).instruction_message()
        introduction = await self.config.guild(guild).introduction_message()
        codeword_r = await self.config.guild(guild).codeword_rules()
        
        time_begin = datetime.datetime.now()
        x = datetime.datetime.now() - time_begin
        

        if self.config.guild(guild).enable_entry() == False:
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

    
                