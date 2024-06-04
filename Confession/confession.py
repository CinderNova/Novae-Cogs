import discord, json, random, datetime, asyncio, os
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager


timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
thumbnail_path = f"{os.path.dirname(__file__)}/thumbnail.png"

class confession(commands.Cog):
    """
    Commands related to confession are managed here.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/debug.log"
        
        self.debug_file = None
        self.identifier = self.bot.user.id
        self.config = Config.get_conf(self, identifier = self.identifier, force_registration=True)
        default_guild = {
            'enable_confession' : True,
            'enable_control_links' : False,
            'enable_debug' : False,
            'enable_check' : False,
            'enable_report' : False,
            'enable_staff_check' : False,
            'confession_channel' : None,
            'control_link_channel' : None,
            'log_channel' : None,
            'staff_role' : None,
            'confessions' : {},
            'control_links' : {},
            'word_blacklist' : []
        }
        self.config.register_guild(**default_guild)

    async def debug_log(self, guild, command, message):
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/{guild.id}-debug.log"
        debug_file = open(debug_file_path, 'a') 

        debug_file.write(f"{datetime.datetime.now()} - Command '{command}': {message}\n")
        debug_file.close()
    
    @commands.group(name="booth")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def booth(self, ctx):
        """ The group of commands related to confession (settings). """
    
    @booth.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_confession(self, ctx, bool: str):
        """ Enable or disable confession. """
        guild = ctx.guild
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_confession' sub-command of 'booth' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_confession.set(True)
            await ctx.send("You have successfully enabled the confession feature.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_confession.set(False)
            await ctx.send("You have successfully disabled the confession feature.")
    
    @booth.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_control_links(self, ctx, bool: str):
        """ Enable or disable Lovense control links. """
        guild = ctx.guild
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_control_links' sub-command of 'booth' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_control_links.set(True)
            await ctx.send("You have successfully enabled the Lovense control link feature.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_control_links.set(False)
            await ctx.send("You have successfully disabled the Lovense control link feature.")

    @booth.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_check(self, ctx, bool: str):
        """ Enable or disable for the bot to check confessions for banned words. """
        guild = ctx.guild

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_check' sub-command of 'booth' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_check.set(True)
            await ctx.send("You have successfully enabled word blacklisting.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_check.set(False)
            await ctx.send("You have successfully disabled word blacklisting.")

    @booth.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_debug(self, ctx, bool: str):
        """Enable or disable debugging."""
        guild = ctx.guild

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_debug' sub-command of 'booth' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_debug.set(True)
            await ctx.send("You have successfully enabled debugging.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_debug.set(False)
            await ctx.send("You have successfully disabled debugging.")
    
    @booth.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_staff_check(self, ctx, bool: str):
        """ Enable or disable the ability for staff to check Lovense control links or confessions, and limits it to Administrators. """
        guild = ctx.guild

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_staff_check' sub-command of 'booth' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_staff_check.set(True)
            await ctx.send("You have successfully enabled staff check.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_staff_check.set(False)
            await ctx.send("You have successfully disabled staff check.")
    
    @booth.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_report(self, ctx, bool: str):
        """ Enable or disable reporting of confessions or control links. """
        guild = ctx.guild

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'enable_report' sub-command of 'booth' command.")
            return

        # Enable or disable confession and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_report.set(True)
            await ctx.send("You have successfully enabled reporting for confessions or links.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_report.set(False)
            await ctx.send("You have successfully disabled reporting for confessions or links.")
    
    @booth.group(name="settings")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        """ The group of commands related to managing the settings (setting the channels and the staff role). """
    
    @settings.group(name="channel")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx):
        """ The group of commands related to managing the channels. """
        
    @settings.group(name="role")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def role(self, ctx):
        """ The group of commands related to managing the role. """
    
    @settings.group(name="blacklist")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx):
        """ The group of commands related to managing the blacklist. """
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def confession(self, ctx, confession: discord.TextChannel):
        """ Set the confession channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'confession' sub-command of 'booth settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).confession_channel.set(confession.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the confession channel to {confession.mention}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def controllink(self, ctx, control_link: discord.TextChannel):
        """ Set the control link channel. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'controllink' sub-command of 'booth settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).control_link_channel.set(control_link.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the control link channel to {control_link.mention}, {author.name}.")
    
    @blacklist.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, word: str):
        """ Add words to the blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' sub-command of 'booth settings blacklist' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).word_blacklist()
        if word in b:
            await ctx.send("This word is already blacklisted.")
            return
        b.append(word)
        await self.config.guild(guild).word_blacklist.set(b)
    
        # Print the message, if successful.
        await ctx.send(f"You have successfully added {word} and set the blacklist to {b}, {author.name}.")
    
    @blacklist.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def list_show(self, ctx):
        """ Show the blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'list_show' sub-command of 'booth settings blacklist' command.")
            return
        
        # Set the blacklist.
        blacklist = await self.config.guild(guild).word_blacklist()
        
        printmessage = "here is the blacklist: \n "
        
        if blacklist == []:
            printmessage+="The blacklist is currently empty."
        else:
            for index in range(0, len(blacklist)-1):
                printmessage += blacklist[index] + ", "
            printmessage += blacklist[len(blacklist)-1]
        
        # Print the message, if successful.
        await ctx.send(f"{author.name}, {printmessage}")
    
    @blacklist.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx):
        """ Clear the blacklist. """
        
        guild = ctx.guild
        author = ctx.message.author
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'clear' sub-command of 'booth settings blacklist' command.")
            return
        
        # Set the blacklist.
        await self.config.guild(guild).word_blacklist.set([])
    
        # Print the message, if successful.
        await ctx.send(f"You have successfully cleared the blacklist, {author.name}.")
    
    @blacklist.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, word: str):
        """ Remove blacklisted words. """
        
        guild = ctx.guild
        author = ctx.message.author
 
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "remove_blacklist", "Running 'remove_blacklist' sub-command of 'booth settings' command.")
            return
        
        # Set the blacklist.
        b = await self.config.guild(guild).word_blacklist()
        if word in b:
            b.remove(word)
            await self.config.guild(guild).word_blacklist.set(b)
        else:
            await ctx.send("My apologies, this word is not in the blacklist.")
            return
    
        # Print the message, if successful.
        await ctx.send(f"You have successfully removed {word} and set the blacklist to {b}, {author.name}.")
    
    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def log(self, ctx, log: discord.TextChannel):
        """ Set the log channel. """
        
        guild = ctx.guild
        author = ctx.message.author

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'log' sub-command of 'booth settings channel' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).log_channel.set(log.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the log channel to {log.mention}, {author.name}.")
    
    @role.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def staff_role(self, ctx, staffrole: discord.Role):
        """ Set the staff role. """
        
        guild = ctx.guild
        author = ctx.message.author
 
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'staff_role' sub-command of 'booth settings role' command.")
            return
        
        # Set the confession channel.
        await self.config.guild(guild).staff_role.set(staffrole.id)
        
        # Print the message, if successful.
        await ctx.send(f"You have successfully set the staff role to {staffrole.mention}, {author.name}.")

    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def show(self, ctx):
        """ View the settings for the Confession Booth. """
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'show' sub-command of 'booth settings' command.")
            return
        
        # Collect all the booleans
        controllinks_bool = await self.config.guild(guild).enable_control_links()
        confession_bool = await self.config.guild(guild).enable_confession()
        debug_bool = await self.config.guild(guild).enable_debug()
        check_bool = await self.config.guild(guild).enable_check()
        staff_check_bool = await self.config.guild(guild).enable_staff_check()
        report_bool = await self.config.guild(guild).enable_report()
        
        
        # Attempt to gather the confession channel
        try:
            confession_channel = get(guild.channels, id= await self.config.guild(guild).confession_channel())
            confession_channel = confession_channel.mention
        except:
            confession_channel = "Not set."
            
        # Attempt to gather the control link channel
        try:
            control_link_channel = get(guild.channels, id= await self.config.guild(guild).control_link_channel())
            control_link_channel = control_link_channel.mention
        except:
            control_link_channel = "Not set."
        
        # Attempt to gather the log channel
        try:
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())
            log_channel = log_channel.mention
        except:
            log_channel = "Not set."
        
        # Attempt to gather the log channel
        try:
            staff_role = get(guild.roles, id= await self.config.guild(guild).staff_role())
            staff_role = staff_role.mention
        except:
            staff_role = "Not set."
        
        settings = f"\n **Enable Confession:** {confession_bool} \n **Enable Report:** {report_bool} \n **Enable Staff Check:** {staff_check_bool}\n**Enable Control Links:** {controllinks_bool} \n **Enable Debugging:** {debug_bool} \n **Enable Check:** {check_bool} \n**Confession Channel:** {confession_channel} \n **Control Link Channel:** {control_link_channel} \n **Log Channel**: {log_channel} \n **Staff Role:** {staff_role}"
        
        embed = discord.Embed(title="Confession Booth: Overview", description=settings, color=clr)
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        await ctx.send(embed=embed)
    
    @settings.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, choice: str=None):
        """ Purge the logs. Add 'confession' or 'control link' to purge only said log, or leave it empty to purge both. """
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
    
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'purge' sub-command of 'booth settings' command.")
            return

        if choice == None:
            await self.config.guild(guild).confessions.set({})
            await self.config.guild(guild).control_links.set({})
            settings = f"\n **Log Purge:** \n The confessions and Lovense control links have been purged."
        
            embed = discord.Embed(title="Confession Booth: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["confession", "confessions", "conf", "booth", "confessing"]:
            await self.config.guild(guild).confessions.set({})
            settings = f"\n **Log Purge:** \n The confessions have been purged."
        
            embed = discord.Embed(title="Confession Booth: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        elif choice.lower() in ["control link", "controllink", "control links", "controllinks", "control", "lovense", "lovense control links", "lovense control", "lovense links"]:
            await self.config.guild(guild).control_links.set({})
            settings = f"\n **Log Purge:** \n The Lovense control links have been purged."
        
            embed = discord.Embed(title="Confession Booth: Update to Logs", description=settings, color=clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            await ctx.send(embed=embed)
        else:
            await ctx.send("My apologies, you have entered the wrong option. Please either leave it empty, choose 'confessions', or 'control links'.")
    
    @app_commands.command(description="Confess something to the server, anonymously or not.")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 30)
    @app_commands.describe(confession="Confess something to the server.", anonymous="You can choose the confession to be anonymous or not. Write yes or no in each case. Leaving it empty will make it anonymous.")
    async def confess(self, interaction: discord.Interaction, confession: str, anonymous: str=None):
        
        """ Confession command that can, or not, check for banned words, and is either anonymous or not. """
        
        # Set the guild, colour, and author
        guild = interaction.guild
        author = interaction.user
        ctx: commands.Context = await self.bot.get_context(interaction)
        clr = await ctx.embed_colour()
        
        # Check if any of the settings have not been properly set yet
        async def check_settings():
            conf = get(guild.channels, id= await self.config.guild(guild).confession_channel())
            logs = get(guild.channels, id= await self.config.guild(guild).log_channel())
            staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
            if conf not in guild.channels or logs not in guild.channels or staffrole not in guild.roles:
                return False
        
        def check_words(blacklist, string):
            for word in blacklist:
                if word.lower() in string.lower():
                    return True, word
            return False, None

        # Check if the function is enabled, if any of the settings are missing, or blacklisted words are used (and cancel the command immediately).
        if not await self.config.guild(guild).enable_confession():
            await interaction.response.send_message(f"My apologies, however, this feature is not currently enabled.", ephemeral=True)
            return
        elif await check_settings():
            await interaction.response.send_message(f"My apologies, however, the necessary information has not been set yet. Consider setting up a log channel, a confession channel, and the staff role. \n Otherwise, I will not be able to fully work or begin to function.", ephemeral=True)
            return
        elif self.config.guild(guild).enable_check():
            blacklist = await self.config.guild(guild).word_blacklist()
            is_bad, forbidden_word = check_words(blacklist, confession)
            if is_bad:
                await interaction.response.send_message(f"My apologies, however, you are using words that are forbidden, namely *'{forbidden_word}'*. Refrain from doing so.", ephemeral=True)
                embed = discord.Embed(title="**Confession Attempt Failed**", description=f"**Member tried to use blacklisted verbiage for a confession** \n\n {author.name} ( {author.mention} / {author.id} ) has attempted to use the word *'{forbidden_word}'* in a confession.", color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await guild.get_channel(await self.config.guild(guild).log_channel()).send(embed=embed)
                return

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'confess' application command of 'confession' cog.")
            return
        
        # Get the current confession dictionary, the number of current confessions + 1, import the channel(s)
        confession_dictionary = await self.config.guild(guild).confessions()
        confession_number = len(confession_dictionary) + 1
        confession_channel = get(guild.channels, id= await self.config.guild(guild).confession_channel())
        
        # Check if the user wants to post it anonymously or not, and post it
        
        if anonymous == None or anonymous.lower() in ["yes", "ye", "ya", "yip", "yup", "yas", "yay"]:
            embed = discord.Embed(title=f"**Confession   -   # {confession_number}**", description = "An unknown soul says, \n\n" + confession, color = clr)
            embed.set_footer(text="Date - {}".format(timestamp))
            thumbnail = discord.File(thumbnail_path, filename = "thumbnail.png")
            embed.set_thumbnail(url="attachment://thumbnail.png")
            msg = await guild.get_channel(confession_channel.id).send(file=thumbnail, embed=embed)
            message_timestamp = msg.created_at.strftime("%A, %d. %B %Y %I:%M%p")
            confession_entry = {
                "confession_id" : confession_number,
                "timestamp" : message_timestamp,
                "member_name" : author.name,
                "member_id" : author.id,
                "message_content" : confession,
                "message_id" : msg.id,
                "message_link" : msg.jump_url,
                "anonymity" : "anonymous" 
            }
            confession_dictionary[confession_number] = confession_entry
            await self.config.guild(guild).confessions.set(confession_dictionary)
            await interaction.response.send_message(f"Your wish is my command, {author.name}. \n The confession has been anonymously sent to {confession_channel.mention}. Do keep in mind that, should it be anything illegal or rule-breaking, I reserve the right to check for whoever is responsible.", ephemeral=True)
       
        elif anonymous.lower() in ["no", "nope", "nah", "na", "nahh", "non't", "nay", "nein", "niet", "njet", "ne", "nen", "nejn"]:
            embed = discord.Embed(title=f"**Confession   -   # {confession_number}**", description = f"{author.name} has confessed to me; their words were: \n" + confession, color = clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            thumbnail = discord.File(thumbnail_path, filename = "thumbnail.png")
            embed.set_thumbnail(url="attachment://thumbnail.png")
            msg = await guild.get_channel(confession_channel.id).send(file=thumbnail, embed=embed)
            message_timestamp = msg.created_at.strftime("%A, %d. %B %Y %I:%M%p")
            confession_entry = {
                "confession_id" : confession_number,
                "timestamp" : message_timestamp,
                "member_name" : author.name,
                "member_id" : author.id,
                "message_content" : confession,
                "message_id" : msg.id,
                "message_link" : msg.jump_url,
                "anonymity" : "public" 
            }
            confession_dictionary[confession_number] = confession_entry
            await self.config.guild(guild).confessions.set(confession_dictionary)
            await interaction.response.send_message(f"Your wish is my command, {author.name}. \n The confession has been sent to {confession_channel.mention}, under your name. Do keep in mind that, should it be anything illegal or rule-breaking, I reserve the right to check for whoever is responsible.", ephemeral=True)
        else:
            await interaction.response.send_message("My apologies, however, you may only enter yes or no - or varieties thereof - to confirm, or deny, whether or not the confession shall be sent anonymously.", ephemeral=True)

    @app_commands.command(description="You can, anonymously or not, send a control link into the channel dedicated for it.")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 20)
    @app_commands.describe(control_link="Paste your Lovense control link here. If it does not contain a control link, the command will not work.", anonymous="You can choose the control link to be sent anonymously or not. Write yes or no in each case.")
    async def control_link(self, interaction: discord.Interaction, control_link: str, anonymous: str=None):
        
        """ Lovense control link command that can be anonymous, or not. """
        
        # Set the guild, colour, and author
        guild = interaction.guild
        author = interaction.user
        ctx: commands.Context = await self.bot.get_context(interaction)
        clr = await ctx.embed_colour()
        
        # Check if any of the settings have not been properly set yet
        async def check_settings():
            contr = get(guild.channels, id= await self.config.guild(guild).control_link_channel())
            logs = get(guild.channels, id= await self.config.guild(guild).log_channel())
            staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
            if contr not in guild.channels or logs not in guild.channels or staffrole not in guild.roles:
                return False
        

        # Check if the function is enabled, if any of the settings are missing, or blacklisted words are used (and cancel the command immediately).
        if not await self.config.guild(guild).enable_control_links():
            await interaction.response.send_message(f"My apologies, however, this feature is not currently enabled.", ephemeral=True)
            return
        elif await check_settings():
            await interaction.response.send_message(f"My apologies, however, the necessary information has not been set yet. Consider setting up a log channel, a confession channel, and the staff role. \n Otherwise, I will not be able to fully work or begin to function.", ephemeral=True)
            return
        elif "https://c.lovense-api.com/" not in control_link:
            await interaction.response.send_message(f"My apologies, however, you have not sent a valid Lovense control link. Please try again, with a proper link.", ephemeral=True)
            return

        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'control_link' application command of 'confession' cog.")
            return
        
        # Get the current confession dictionary, the number of current confessions + 1, import the channel(s)
        control_dictionary = await self.config.guild(guild).control_links()
        control_link_channel = get(guild.channels, id= await self.config.guild(guild).control_link_channel())
        controllink_number = len(control_dictionary) + 1
        
        # Check if the user wants to post it anonymously or not, and post it
        
        if anonymous == None or anonymous.lower() in ["yes", "ye", "ya", "yip", "yup", "yas", "yay"]:
            embed = discord.Embed(title=f"**Lovense Control Link  -  #{controllink_number}**", description = f"*It is said an anonymous soul wants a toy of theirs under control; Namely,* \n" + control_link, color = clr)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            msg = await guild.get_channel(control_link_channel.id).send(embed=embed)
            message_timestamp = msg.created_at.strftime("%A, %d. %B %Y %I:%M%p")
            control_entry = {
                "cl_id" : controllink_number,
                "timestamp" : message_timestamp,
                "member_name" : author.name,
                "member_id" : author.id,
                "message_content" : control_link,
                "message_id" : msg.id,
                "message_link" : msg.jump_url,
                "anonymity" : "anonymous" 
            }
            control_dictionary[controllink_number] = control_entry
            await self.config.guild(guild).control_links.set(control_dictionary)
            await interaction.response.send_message(f"Your wish is my command, {author.name}. \n The Lovense control link has been sent to {control_link_channel.mention}, anonymously. Do keep in mind that, should it be anything illegal or rule-breaking, I reserve the right to check for whoever is responsible.", ephemeral=True)
        elif anonymous.lower() in ["no", "nope", "nah", "na", "nahh", "non't", "nay", "nein", "niet", "njet", "ne", "nen", "nejn"]:
            embed = discord.Embed(title=f"**Lovense Control Link  -  #{controllink_number}**", description = f"*It is said {author.name} wants a toy of theirs under control; Namely,* \n" + control_link, color = clr)
            embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
            embed.set_footer(text="Date - {}".format(timestamp))
            
            msg = await guild.get_channel(control_link_channel.id).send(embed=embed)
            message_timestamp = msg.created_at.strftime("%A, %d. %B %Y %I:%M%p")
            control_entry = {
                "cl_id" : controllink_number,
                "timestamp" : message_timestamp,
                "member_name" : author.name,
                "member_id" : author.id,
                "message_content" : control_link,
                "message_id" : msg.id,
                "message_link" : msg.jump_url,
                "anonymity" : "public" 
            }
            control_dictionary[controllink_number] = control_entry
            await self.config.guild(guild).control_links.set(control_dictionary)
            await interaction.response.send_message(f"Your wish is my command, {author.name}. \n The Lovense control link has been sent to {control_link_channel.mention}, under your name. Do keep in mind that, should it be anything illegal or rule-breaking, I reserve the right to check for whoever is responsible.", ephemeral=True)
        else:
            await interaction.response.send_message("My apologies, however, you may only enter yes or no - or varieties thereof - to confirm, or deny, whether or not the confession shall be sent anonymously.", ephemeral=True)

    @app_commands.command(description="Report a certain confession with a reason.")
    @app_commands.guild_only()
    @app_commands.describe(choice="Choose either confession or control link.",id_number="The number of the confession / control which you want to report.", reason="The reason for your report.")
    async def booth_report(self, interaction: discord.Interaction, choice: str, id_number: int, reason: str):
        
        """ A command to report a confession or Lovense control link. """
        
        guild = interaction.guild
        author = interaction.user
        ctx: commands.Context = await self.bot.get_context(interaction)
        clr = await ctx.embed_colour()
        target = None
        
        # Check if any of the settings have not been properly set yet
        async def check_settings():
            conf = get(guild.channels, id= await self.config.guild(guild).confession_channel())
            logs = get(guild.channels, id= await self.config.guild(guild).log_channel())
            staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
            if conf not in guild.channels or logs not in guild.channels or staffrole not in guild.roles:
                return False

        # Check if the function is enabled, if any of the settings are missing, or blacklisted words are used (and cancel the command immediately).
        if not await self.config.guild(guild).enable_report():
            await interaction.response.send_message(f"My apologies, however, this feature is not currently enabled.", ephemeral=True)
            return
        elif await check_settings():
            await interaction.response.send_message(f"My apologies, however, the necessary information has not been set yet. Consider setting up a log channel, a confession channel, and the staff role. \n Otherwise, I will not be able to fully work or begin to function.", ephemeral=True)
            return

        if choice.lower in ["confession", "conf", "confess", "booth", "confessing"]:
            
            confessions = await self.config.guild(guild).confessions()
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())
            staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
            
            for key in confessions:
                if confessions[key]["confession_id"] == id_number:
                    target = confessions[key]
                    
            if target == None:
                await interaction.response.send_message("My apologies, however, the mentioned confession ID has not been found in the database.", ephemeral=True)
                return

            
            if get(guild.members, id=target["member_id"]) == None:
                await interaction.response.send_message(f"You have successfully reported the confession, {author.name}.", ephemeral=True)
                textmessage = f"Attention, \n a member has reported confession #{target['confession_id']}. \n **Confession Date:** {target['timestamp']}\n **Member:** {target['member_name']} ({target['member_id']}) \n **Content:** {target['message_content']} \n **Anonymity:** {target['anonymity']} \n **Message Link:** {target['message_link']}"
                embed = discord.Embed(title="**Confession Booth: Report**", description=f"Attention {staffrole.mention}, " + textmessage + f"\n Reporting Member: {author.name} ({author.id} / {author.mention})", color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.get_channel(log_channel.id).send(embed=embed)
            else:
                await interaction.response.send_message(f"You have successfully reported the confession, {author.name}.", ephemeral=True)
                member = get(guild.members, id=target["member_id"])
                textmessage = f"Attention, \n a member has reported confession #{target['confession_i']}. \n **Confession Date:** {target['timestamp']}\n **Member:** {member.name} ({member.id} / {member.mention}) \n **Content:** {target['message_content']} \n **Anonymity:** {target['anonymity']} \n **Message Link:** {target['message_link']}"
                embed = discord.Embed(title="**Confession Booth: Report**", description=f"Attention {staffrole.mention}, " + textmessage + f"\n Reporting Member: {author.name} ({author.id} / {author.mention})", color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.get_channel(log_channel.id).send(embed=embed)

            # Debug Statement
            if await self.config.guild(guild).enable_debug():
                await self.debug_log(guild, "add", "Running 'booth_report' application command of 'confession' cog.")
                return
            
        elif choice.lower in ["lovense", "control", "lovense control", "control link", "lovense control link", "control links", "controllink", "controllinks", "lovense controllink", "lovense link"]:
            
            control_links = await self.config.guild(guild).control_links()
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())
            staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
            
            for key in control_links:
                if control_links[key]["cl_id"] == id_number:
                    target = control_links[key]
                    
            if target == None:
                await interaction.response.send_message("My apologies, however, the mentioned control link ID has not been found in the database.", ephemeral=True)
                return

            
            if get(guild.members, id=target["member_id"]) == None:
                await interaction.response.send_message(f"You have successfully reported the control link, {author.name}.", ephemeral=True)
                textmessage = f"Attention, \n a member has reported control link #{target['cl_id']}. \n Control Link Date: {target['timestamp']}\n Member: {target['member_name']} ({target['member_id']}) \n Content: {target['message_content']} \n Anonymity: {target['anonymity']} \nMessage Link: {target['message_linl']}"
                embed = discord.Embed(title="**Control Link Booth: Report**", description=f"Attention {staffrole.mention}, " + textmessage + f"\n Reporting Member: {author.name} ({author.id} / {author.mention})", color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.get_channel(log_channel.id).send(embed=embed)
            else:
                await interaction.response.send_message(f"You have successfully reported the control link, {author.name}.", ephemeral=True)
                member = get(guild.members, id=target["member_id"])
                textmessage = f"Attention, \n a member has reported control link #{target['confession_id']}. \n Confession Date: {target['timestamp']}\n Member: {member.name} ({member.id} / {member.mention}) \n Content: {target['message_content']} \n Anonymity: {target['anonymity']} \nMessage Link: {target['message_link']}"
                embed = discord.Embed(title="**Control Link Booth: Report**", description=f"Attention {staffrole.mention}, " + textmessage + f"\n Reporting Member: {author.name} ({author.id} / {author.mention})", color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.get_channel(log_channel.id).send(embed=embed)

            # Debug Statement
            if await self.config.guild(guild).enable_debug():
                await self.debug_log(guild, "add", "Running 'booth_report' application command of 'confession' cog.")
                return
        else:
            await interaction.response.send_message(f"My apologies, I require a choice that is either 'confession', or 'control link'.", ephemeral=True)
            return

    @app_commands.command(description="[staff] Collects the user behind a confession or control link.")
    @app_commands.guild_only()
    @app_commands.describe(choice="Choose either confession or control link.",id_number="The number of the confession / control which you want to report.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def booth_check(self, interaction: discord.Interaction, choice: str, id_number: int):
        
        """ A command to report a confession or Lovense control link. """
        
        guild = interaction.guild
        author = interaction.user
        ctx: commands.Context = await self.bot.get_context(interaction)
        clr = await ctx.embed_colour()
        target = None
        nostaff = False
        
        # Check if any of the settings have not been properly set yet
        async def check_settings():
            conf = get(guild.channels, id= await self.config.guild(guild).confession_channel())
            contr = get(guild.channels, id= await self.config.guild(guild).control_link_channel())
            logs = get(guild.channels, id= await self.config.guild(guild).log_channel())
            staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
            if conf not in guild.channels or logs not in guild.channels or contr not in guild.channels or staffrole not in guild.roles:
                return False

        # Check if the function is enabled, if any of the settings are missing, or blacklisted words are used (and cancel the command immediately).
        if not await self.config.guild(guild).enable_staff_check():
            nostaff = True
            if not author.guild_permissions.administrator:
                await interaction.response.send_message(f"My apologies, however, this feature is only enabled for administrators.",ephemeral=True)
                return
        elif await check_settings():
            await interaction.response.send_message(f"My apologies, however, the necessary information has not been set yet. Consider setting up a log channel, a confession channel, and the staff role. \n Otherwise, I will not be able to fully work or begin to function.", ephemeral=True)
            return
                
        staffrole = get(guild.roles, id = await self.config.guild(guild).staff_role())
        if staffrole not in author.roles:
            await interaction.response.send_message("My apologies, however, you do not have the necessary permission to execute this function.", ephemeral=True)
            return
                
        if choice.lower() in ["confession", "conf", "confess", "booth", "confessing"]:
            
            confessions = await self.config.guild(guild).confessions()
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())
            
                
            for key in confessions:
                if confessions[key]["confession_id"] == id_number:
                    target = confessions[key]
                    
            if target == None:
                await interaction.response.send_message("My apologies, however, the mentioned confession ID has not been found in the database.", ephemeral=True)
                return

            
            if get(guild.members, id=target["member_id"]) == None:
                textmessage = f"Dear, the confession #{target['confession_id']} you asked for is here: \n **Confession Date:** {target['timestamp']}\n **Member:** {target['member_name']} ({target['member_id']}) \n **Content:** {target['message_content']} \n **Anonymity:** {target['anonymity']} \n **Message Link:** {target['message_link']}"
                embed = discord.Embed(title="**Confession Booth: Staff Check**", description=textmessage, color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                member = get(guild.members, id=target["member_id"])
                textmessage = f"Dear, the confession #{target['confession_id']} you asked for is here: \n **Confession Date:** {target['timestamp']}\n **Member:** {member.name} ({member.id} / {member.mention}) \n **Content:** {target['message_content']} \n **Anonymity:** {target['anonymity']} \n **Message Link:** {target['message_link']}"
                embed = discord.Embed(title="**Confession Booth: Staff Check**", description=textmessage, color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.response.send_message(embed=embed, ephemeral=True)

            # Debug Statement
            if await self.config.guild(guild).enable_debug():
                await self.debug_log(guild, "add", "Running 'booth_check' application command of 'confession' cog.")
                return
            
        elif choice.lower() in ["lovense", "control", "lovense control", "control link", "lovense control link", "control links", "controllink", "controllinks", "lovense controllink", "lovense link"]:
            
            control_links = await self.config.guild(guild).control_links()
            log_channel = get(guild.channels, id= await self.config.guild(guild).log_channel())

            
            for key in control_links:
                if control_links[key]["cl_id"] == id_number:
                    target = control_links[key]
                    
            if target == None:
                await interaction.response.send_message("My apologies, however, the mentioned control link ID has not been found in the database.", ephemeral=True)
                return

            
            if get(guild.members, id=target["member_id"]) == None:
                textmessage = f"Dear, control link #{target['cl_id']} is the following. \n **Control Link Date:** {target['timestamp']}\n **Member:** {target['member_name']} ({target['member_id']}) \n **Content:** {target['message_content']} \n **Anonymity:** {target['anonymity']} \n **Message Link:** {target['message_link']}"
                embed = discord.Embed(title="**Control Link Booth: Staff Check**", description=f"Attention {staffrole.mention}, " + textmessage, color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.get_channel(log_channel.id).send(embed=embed)
            else:
                member = get(guild.members, id=target["member_id"])
                textmessage = f"Dear, control link #{target['cl_id']} is the following. \n **Control Link Date:** {target['timestamp']}\n **Member:** {member.name} ({member.id} / {member.mention}) \n **Content:** {target['message_content']} \n **Anonymity:** {target['anonymity']} \n **Message Link:** {target['message_link']}"
                embed = discord.Embed(title="**Control Link Booth: Staff Check**", description=textmessage, color=clr)
                embed.set_footer(text="Date - {}".format(timestamp))
                await interaction.response.send_message(embed=embed, ephemeral=True)

            # Debug Statement
            if await self.config.guild(guild).enable_debug():
                await self.debug_log(guild, "add", "Running 'booth_check' application command of 'confession' cog.")
                return
        else:
            await interaction.response.send_message(f"My apologies, I require a choice that is either 'confession', or 'control link'.", ephemeral=True)
            return


