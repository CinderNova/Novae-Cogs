import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
from hmtaipy import pyhmtai
import redbot.core.data_manager
import requests


# Set the timestamp as of the time of the command.
timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
giflist = "/home/aimonomia/discord/akarin/akarin_files/cogs/CogManager/cogs/theatre/cmdgifs.json"





class theatre(commands.Cog):
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
            'enable_blacklist' : False,
            'enable_debug' : False,
            'enable_nsfw' : False,
            'channel_blacklist' : [],
            'default_cooldown' : 5, # in seconds
        }
        self.config.register_guild(**default_guild)

    
    
    async def debug_log(self, guild, command, message):
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/{guild.id}-debug.log"
        debug_file = open(debug_file_path, 'a') 
        debug_file.write(f"{datetime.datetime.now()} - Command '{command}': {message}\n")
        debug_file.close()
    
    @commands.group(name="theatre")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def theatre(self, ctx):
        """The group of commands related to Theatre."""
    
    @theatre.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def view_settings(self, ctx):
        """View the settings for Theatre."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "view", "Running 'view' sub-command of 'theatre' command.")
            return
        
        # Make a clean embed, send it to the local channel.
        cd = await self.config.guild(guild).default_cooldown()
        nsfw = await self.config.guild(guild).enable_nsfw()
        debug = await self.config.guild(guild).enable_debug()
        blacklist = await self.config.guild(guild).enable_blacklist()
        settings = f"\n **Cooldown:** {cd} (in seconds)\n **Enable Blacklist:** {blacklist} \n **Enable NSFW commands:** {nsfw} \n **Enable Debugging:** {debug}"
        embed = discord.Embed(title="Theatre: Overview", description=settings, color=clr)
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        await ctx.send(embed=embed)
        
    @theatre.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_nsfw(self, ctx, bool: str):
        """Enable or disable NSFW commands (in NSFW channels marked as such)."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "", "Running 'nsfw' sub-command of 'theatre' command.")
            return

        # Enable or disable NSFW commands and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_nsfw.set(True)
            await ctx.send("You have successfully enabled NSFW commands.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_nsfw.set(False)
            await ctx.send("You have successfully disabled NSFW commands.")
    
    @theatre.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_blacklist(self, ctx, bool: str):
        """Enable or disable the blacklist."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "enable_blacklist", "Running 'enable_blacklist' sub-command of 'theatre' command.")
            return
        
        # Enable or disable the blacklist and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_blacklist.set(True)
            await ctx.send("You have successfully enabled the blacklist.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_blacklist.set(False)
            await ctx.send("You have successfully disabled the blacklist.")
        
    @theatre.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable_debug(self, ctx, bool: str):
        """Enable or disable Debugging."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "enable_debug", "Running 'enable_debug' sub-command of 'theatre' command.")
            return

        # Enable or disable dbugging and print it to the local channel.
        if bool in ["True", "true", "enable", "Enable"]:
            await self.config.guild(guild).enable_debug.set(True)
            await ctx.send("You have successfully debugging.")
        elif bool in ["False", "false", "disable", "Disable"]:
            await self.config.guild(guild).enable_debug.set(False)
            await ctx.send("You have successfully enabled debugging.")
    
    @theatre.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cooldown(self, ctx, cd: int):
        """Edit the command cooldown (in seconds)."""
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "cooldown", "Running 'cooldown' sub-command of 'theatre' command.")
            return
        
        # Check the cooldown given.
        if cd < 0:
            cd = abs(cd)
        elif cd == 0:
            await ctx.send("You can only set the cooldown to values bigger than or equal to 1.")
            return
        
        # Print the message, if successful.
        if cd == 1:
            await self.config.guild(guild).default_cooldown.set(cd)
            await ctx.send(f"You have successfully changed the cooldown to {cd} second.")
        else:
            await self.config.guild(guild).default_cooldown.set(cd)
            await ctx.send(f"You have successfully changed the cooldown to {cd} seconds.")

    @theatre.group(name="blacklist")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx):
        """Below are commands related to blacklisting channels. Blacklisted channels will not allow Theatre commands."""
        
    @blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, channel: discord.TextChannel):
        """Add a channel to the Theatre blacklist."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "add", "Running 'add' sub-command of 'theatre blacklist' command.")
            return
        
        # Add the channel(-ID) to the blacklist if the channel is not already part of it.
        channellist = await self.config.guild(guild).channel_blacklist()
        if channel.id in channellist:
            await ctx.send(f"My apologies, {author.name}. The channel {channel.mention} is already blacklisted.")
            return
        
        channellist.append(channel.id)
        await self.config.guild(guild).channel_blacklist.set(channellist)
        
        # Now we want to have a clean list of blacklisted channels, so:
        printmessage = "\n\n\n **Updated Blacklist:** \n\n"
        for ch in channellist:
            if get(guild.channels, id=ch) != None:
                chan = get(guild.channels, id=ch)
                printmessage+= f"{chan.mention} \n"
            else:
                await ctx.send("There has been an error. One of the given channel IDs is not channel-type.")

        # Make a clean embed, send it to the local channel.
        embed = discord.Embed(title="Theatre: Channel Blacklist", description=f"The channel blacklist for Theatre has been updated. \n\n {channel.mention} has been added successfully." + printmessage, color=clr)
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        await ctx.send(embed=embed)
    
    @blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, channel: discord.TextChannel):
        """Remove a channel from the Theatre blacklist."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "remove", "Running 'remove' sub-command of 'theatre blacklist' command.")
            return
        
        # Remove the channel from the list.
        channellist = await self.config.guild(guild).channel_blacklist()
        if channel.id not in channellist:
            await ctx.send("My apologies, this channel is not blacklisted. I could not follow your command.")
            return
        
        channellist.remove(channel.id)
        await self.config.guild(guild).channel_blacklist.set(channellist)
        
        # Now we want to have a clean list of blacklisted channels, so:
        printmessage = "\n\n\n **Updated Blacklist:** \n\n"

        D = len(channellist)
        
        if D == 0:
            printmessage += "There are no blacklisted channels."
        else:
            for i in range(0,D-1):
                if get(guild.channels, id=channellist[i]) != None and i<(D-1):
                    chan = get(guild.channels, id=channellist[i])
                    printmessage+= f"{chan.mention} \n"
                else:
                    await ctx.send(f"There has been an error. One of the given channel IDs is not channel-type (ID = {channellist[i]}).")
            if get(guild.channels, id=channellist[D-1]) != None:
                    chan = get(guild.channels, id=channellist[D-1])
                    printmessage+= f"{chan.mention}"
            else:
                await ctx.send(f"There has been an error. One of the given channel IDs is not channel-type (ID = {channellist[D-1]}).")

        # Make a clean embed, send it to the local channel.
        embed = discord.Embed(title="Theatre: Channel Blacklist", description=f"The channel blacklist for Theatre has been updated. \n\n {channel.mention} has been removed successfully. " + printmessage, color=clr)
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        await ctx.send(embed=embed)
    
    @blacklist.command(name="purge")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx):
        """Purge the Theatre blacklist."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "purge", "Running 'purge' sub-command of 'theatre blacklist' command.")
            return
        
        # Purge the blacklist.
        await self.config.guild(guild).channel_blacklist.set([])
        
        # Now we want to have a clean list of blacklisted channels. Since it is empty,
        printmessage = "\n\n\n **Updated Blacklist:** \n\n Empty."

        # Make a clean embed, send it to the local channel.
        embed = discord.Embed(title="Theatre: Channel Blacklist", description=f"The channel blacklist for Theatre has been updated. \n\n" + printmessage, color=clr)
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        await ctx.send(embed=embed)
    
    @blacklist.command(name="view")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def view(self, ctx):
        """Remove a channel from the Theatre blacklist."""
        
        guild = ctx.guild
        author = ctx.message.author
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, "view", "Running 'view' sub-command of 'theatre blacklist' command.")
            return
        
        # Remove the channel from the list.
        channellist = await self.config.guild(guild).channel_blacklist()

        # Now we want to have a clean list of blacklisted channels, so we arrange it,
        printmessage = "\n\n\n **Blacklist:** \n\n"

        D = len(channellist)
        
        if D == 0:
            printmessage += "There are no blacklisted channels."
        else:
            # until D-1
            for i in range(0,D-1):
                if get(guild.channels, id=channellist[i]) != None and i<(D-1):
                    chan = get(guild.channels, id=channellist[i])
                    printmessage+= f"{chan.mention} \n"
                else:
                    await ctx.send(f"There has been an error. One of the given channel IDs is not channel-type (ID = {channellist[i]}).")
            # for D-1, we separate,
            if get(guild.channels, id=channellist[D-1]) != None:
                    chan = get(guild.channels, id=channellist[D-1])
                    printmessage+= f"{chan.mention}"
            else:
                await ctx.send(f"There has been an error. One of the given channel IDs is not channel-type (ID = {channellist[D-1]}).")

        # Make a clean embed, send it to the local channel.
        embed = discord.Embed(title="Theatre: Channel Blacklist", description=f"The channel blacklist for Theatre is the following:" + printmessage, color=clr)
        embed.set_author(name=" - Requested by {} - ".format(author), icon_url=author.display_avatar.url)
        embed.set_footer(text="Date - {}".format(timestamp))
        await ctx.send(embed=embed)
    
    
    @app_commands.command(description="Hug a user.")
    @app_commands.user_install()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(member="The user you wish to hug.")
    async def hugs(self, interaction: discord.Interaction, member: discord.User):
        
        """ Hug a member. """
        
        guild = interaction.guild
        author = interaction.user
        clr = 0xffae42
        category = "hug"
        
        action_list = [f"{member.mention} got hugged by {author.mention}, cute!",
                       f"{author.mention} gently hugs {member.mention}.",
                       f"{member.mention} is pulled into an embrace by {author.mention}.",
                       f"{author.mention} decides to hug {member.mention} tight, but doesn't let go. So adorable~",
                       f"{author.mention} gives their biggest hug to {member.mention}!"]
        

        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif member != None:
            
            # Random number to pick a gif.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(description="Kiss a user.")
    @app_commands.user_install()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(member="The user you wish to kiss.")
    async def kisses(self, interaction: discord.Interaction, member: discord.User):
        
        """ Hug a member. """
        
        guild = interaction.guild
        author = interaction.user
        clr = 0xffae42
        category = "kiss"
        
        A = f"{author.mention}"
        B = f"{member.mention}"
        action_list = [
                    f"{A} kisses {B} gently. Their lips meet and won't part~",
                    f"{B} gets a soft kiss from {A}. They are cute.",
                    f"{B} blushes after being blown a kiss from {A}.",
                    f"{B} and {A} are kissing so intimately.",
                    f"{A} lavishly kissies {B}'s lips."
                ]

        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif member != None:
            
            # Random number to pick a gif.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(description="Shoot a user.")
    @app_commands.user_install()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(member="The user you wish to shoot.")
    async def fire(self, interaction: discord.Interaction, member: discord.User):
        
        """ Shoot a member. """
        
        guild = interaction.guild
        author = interaction.user
        clr = 0xffae42
        category = "shoot"
        
        A = f"{author.mention}"
        B = f"{member.mention}"
        action_list = [
                    f"{A} shoots {B}. They're dead.",
                    f"{B} is being judged by {A}. Death Sentence!",
                    f"{A} cocks the gun and shoots {B}. They missed. Weakness!",
                    f"{B} evades the shots {A} takes at them. "
                ]

        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif member != None:
            
            # Random number to pick a gif.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(description="Dropkick a user.")
    @app_commands.user_install()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(member="The user you wish to dropkick.")
    async def kickdown(self, interaction: discord.Interaction, member: discord.User):
        
        """ Dropkick a member. """
        
        guild = interaction.guild
        author = interaction.user
        clr = 0xffae42
        category = "kick"
        
        A = f"{author.mention}"
        B = f"{member.mention}"
        action_list = [
                    f"{A} kicks {B} and breaks their bones. Ouch.",
                    f"{B} is dropkicked by {A}.",
                    f"{A} kicks {B}'s legs. Go down already!",
                    f"{B} gets kicked to the ground by {A}."
                ]
        

        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif member != None:
            
            # Random number to pick a gif.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(description="Bonk a user.")
    @app_commands.user_install()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(member="The user you wish to bonk.")
    async def hornybonk(self, interaction: discord.Interaction, member: discord.User):
        
        """ Bonk a member. """
        
        guild = interaction.guild
        author = interaction.user
        clr = 0xffae42
        category = "bonk"
        hmtai = pyhmtai()
        
        A = f"{author.mention}"
        B = f"{member.mention}"
        action_list = [
                    f"{A} bonks {B} with a baseball bat. Ouch!",
                    f"{B} is being bonked by {A}.",
                    f"{A} bonks {A} because they're horny.",
                    f"{A} sends {B} to horny jail!" 
                ]

        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif member != None:
            
            # Random number to pick a gif.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            link = hmtai.sfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await interaction.response.send_message(embed=embed)
    
    

    

    # SAFE FOR WORK
    
    
    @commands.command(name="hug")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def hug(self, ctx, member: discord.Member=None):
        """ Hug a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "hug"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            action_list = [
                        f"{member.mention} got hugged by {author.mention}, cute!",
                        f"{author.mention} gently hugs {member.mention}.",
                        f"{member.mention} is pulled into an embrace by {author.mention}.",
                        f"{author.mention} decides to hug {member.mention} tight, but doesn't let go. So adorable~",
                        f"{author.mention} gives their biggest hug to {member.mention}!"
                       ]
            
            
            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="cuddle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cuddle(self, ctx, member: discord.Member=None):
        """ Cuddle a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "cuddle"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            
            action_list = [
                f"{member.mention} got cuddled by {author.mention}, cute!",
                f"{author.mention} gently cuddles up to {member.mention}.",
                f"{member.mention} is pulled into a cuddle puddle by {author.mention}.",
                f"{author.mention} cuddles {member.mention} to death. So adorable~"
                ]
            

            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="kiss")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def kiss(self, ctx, member: discord.Member=None):
        """ Kiss a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "kiss"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} kisses {B} gently. Their lips meet and won't part~",
                    f"{B} gets a soft kiss from {A}. They are cute.",
                    f"{B} blushes after being blown a kiss from {A}.",
                    f"{B} and {A} are kissing so intimately.",
                    f"{A} lavishly kissies {B}'s lips."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="handhold")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def handhold(self, ctx, member: discord.Member=None):
        """ Hold a member's hand. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "handhold"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            action_list = [
                f"{author.mention} picks {member.mention}'s hand and squeezes it. So sweet~",
                f"{member.mention} blushes after {author.mention} takes their hand.",
                f"{author.mention} caresses {member.mention}'s hand. Cute!",
                f"{member.mention}'s fingers intertwine with {author.mention}'s. How adorable~"
                ]
            

            
            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="bite")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bite(self, ctx, member: discord.Member=None):
        """ Bite a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "bite"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} bites {B}'s hand. Their teeth marks show!",
                    f"{B} gets nibbled by {A}.",
                    f"{B} is annoyed at {A} biting their finger.",
                    f"{B} and {A} are biting and fighting."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="tickle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def tickle(self, ctx, member: discord.Member=None):
        """ Tickle a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "tickle"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} tickles the sides of {B}! Now they are wrestling.",
                    f"{B} is surprised by the tickle attack of {A}.",
                    f"{B} gets tickled all over by {A}.",
                    f"{B} has their feet tickled by {A}."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="highfive")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def highfive(self, ctx, member: discord.Member=None):
        """ Highfive a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "highfive"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} highfives {B} after praising them.",
                    f"{B} is getting a highfive from {A}.",
                    f"{B} is surprised by the highfive to the back of their head from {A}.",
                    f"{A} throws {B} a highfive. They miss the cue."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="wink")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def wink(self, ctx, member: discord.Member=None):
        """ Wink at a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "wink"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} winks at {B}.",
                    f"{B} is getting looks from {A}.",
                    f"{B} is being thrown a wink by {A}. So dirty-minded!",
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="shoot")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def shoot(self, ctx, member: discord.Member=None):
        """ Shoot a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "shoot"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} shoots {B}. They're dead.",
                    f"{B} is being judged by {A}. Death Sentence!",
                    f"{A} cocks the gun and shoots {B}. They missed. Weakness!",
                    f"{B} evades the shots {A} takes at them. "
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="slap")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def slap(self, ctx, member: discord.Member=None):
        """ Slap a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "slap"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} slaps {B} straight in the face. They died. Oopsie!",
                    f"{B} is being chased by {A} trying to slap them.",
                    f"{A} slaps {B}'s butt. Wooey!",
                    f"{B} dodges the slaps from {A} and slaps them instead!"
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="pat")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member=None):
        """ Pat a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "pat"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} pats {B}. There, there. Everything will be okay.",
                    f"{B} is being pet by {A}.",
                    f"{A} gently pats {B}'s head. Adorable~",
                    f"{B} melts away from the pats of {A}."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="dropkick")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def dropkick(self, ctx, member: discord.Member=None):
        """ Dropkick a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "kick"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} kicks {B} and breaks their bones. Ouch.",
                    f"{B} is dropkicked by {A}.",
                    f"{A} kicks {B}'s legs. Go down already!",
                    f"{B} gets kicked to the ground by {A}."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="poke")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def poke(self, ctx, member: discord.Member=None):
        """ Poke a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "poke"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} pokes {B}. Attention pleaseee!",
                    f"{B} getting poked by {A}.",
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="throw")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def throw(self, ctx, member: discord.Member=None):
        """ Throw a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "yeet"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} throws {B} away.",
                    f"{B} gets thrown around by {A}.",
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="thumbsup")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def thumbsup(self, ctx, member: discord.Member=None):
        """ Give a member thumbs up. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "thumbsup"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} gives {B} a thumbsup.",
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="punch")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def punch(self, ctx, member: discord.Member=None):
        """ Punch a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "punch"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} punches {B} in the balls.",
                    f"{B} has their gut punched by {A}.",
                    f"{A} throws punches at {B}."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="stare")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def stare(self, ctx, member: discord.Member=None):
        """ Stare at a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "stare"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} stares at {B} from afar.",
                    f"{B} is being watched by {A}. They're uncomfortable now.",
                    f"{A} throws shade at {B}."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="wave")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def wave(self, ctx, member: discord.Member=None):
        """ Wave at a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "wave"

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} waves at {B} from afar. Hello there!",
                    f"{B} is being waved at by {A}.",
                    f"{A} waves for {B} to come over."
                ]


            resp = requests.get(f"https://nekos.best/api/v2/{category}")
            link = resp.json()
            link = link["results"][0]["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="bonk")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bonk(self, ctx, member: discord.Member=None):
        """ Bonk a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "bonk"
        hmtai = pyhmtai()
        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} bonks {B} with a baseball bat. Ouch!",
                    f"{B} is being bonked by {A}.",
                    f"{A} bonks {A} because they're horny.",
                    f"{A} sends {B} to horny jail!" 
                ]

            link = hmtai.sfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="bully")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bully(self, ctx, member: discord.Member=None):
        """ Bully a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "bully"
        hmtai = pyhmtai()
        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} bullies {B}. Teehee!",
                    f"{B} is being bullied by {A}.",
                ]

            link = hmtai.sfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="lick")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def lick(self, ctx, member: discord.Member=None):
        """ Lick a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "lick"
        hmtai = pyhmtai()
        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} licks {B} all over. Naughty!",
                    f"{B} is being licked by {A}.",
                ]

            link = hmtai.sfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="boop")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def boop(self, ctx, member: discord.Member=None):
        """ Boop a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "boop"
        hmtai = pyhmtai()
        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} boops {B}'s nose.",
                    f"{B} is being booped by {A}.",
                ]

            link = hmtai.sfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="kill")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def kill(self, ctx, member: discord.Member=None):
        """ Kill a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "kill"
        hmtai = pyhmtai()
        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                    f"{A} kills {B}. Die!",
                    f"{A} says they will kill {B} so hard, that they'll die to death.",
                ]

            link = hmtai.sfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]
            
            # Random number to pick a gif.
            action_length = len(action_list)
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    

            randomaction = random.randint(0,action_length-1)
            
            
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    
    
    
    # Single member ones
    
    @commands.command(name="cry")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cry(self, ctx):
        """ Cry. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "cry"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} cries all alone. Someone comfort them!",
                    f"{A} starts sobbing. What's up, dear?",
                    f"{A}'s tears roll down their cheeks. You're safe, darling."
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="blush")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def blush(self, ctx):
        """ Blush. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "blush"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} blushes bright red. Their face is so cute!",
                    f"{A}'s face has become red like a tomato. Naww!",
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="pout")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def pout(self, ctx):
        """ Pout. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "pout"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} pouts in a corner.",
                    f"{A}'s pouting phase is so cute!",
                    f"{A} has been pouting for a while now~"
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="dance")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def dance(self, ctx):
        """ Dance. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "dance"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} is dancing all over the place. Disco much?",
                    f"{A} breakdances on the floor. Careful!",
                    f"{A} wipes the floor with everyone when it comes to dancing!"
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="facepalm")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def facepalm(self, ctx):
        """ Facepalm. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "facepalm"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} facepalms. How cringe.",
                    f"{A} is cringing at the sight in front of them.",
                    f"{A} dies of cringe immediately."
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="lurk")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def lurk(self, ctx):
        """ Lurk. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "lurk"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} is lurking around. Shady!",
                    f"{A} lurks the chat. Suspicious much!",
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="nod")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def nod(self, ctx):
        """ Nod. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "nod"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} nods. They understand.",
                    f"{A} agrees.",
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="nope")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def nope(self, ctx):
        """ Nope. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "nope"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} nopes the fuck out.",
                    f"{A} disagrees.",
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="shrug")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def shrug(self, ctx):
        """ Shrug. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "shrug"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} shrugs. Who cares?",
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="smug")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def smug(self, ctx):
        """ Smug. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "smug"
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} is so smug."
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="nosebleed")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def nosebleed(self, ctx):
        """ Nosebleed. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "nosebleed"
        hmtai = pyhmtai()
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        A = f"{author.mention}"
        action_list = [
                    f"{A} gets a nosebleed. Lewd!"
                ]


        resp = requests.get(f"https://nekos.best/api/v2/{category}")
        link = resp.json()
        link = link["results"][0]["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    







    @commands.command(name="uppie")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def uppie(self, ctx, member: discord.Member=None):
        """ Uppie a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "uppie"
        perform = "being uppied by"
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you mentioned yourself. Please choose another.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            # Random number to pick a gif.
            if member_ult in guild.members:
                length = len(sfwcategories[category])
            else:
                return
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
            randompick = random.randint(0, length - 1)
            
            # Add '.gif' to make it a proper gif, otherwise it will not load.
            link = sfwcategories[category][randompick]
            link = link + ".gif"
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. And up you go!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="tuck")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def tuck(self, ctx, member: discord.Member=None):
        """ Tuck a member into bed and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "tuck"
        perform = "being tucked in by"
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you mentioned yourself. Please choose another.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            # Random number to pick a gif.
            if member_ult in guild.members:
                length = len(sfwcategories[category])
            else:
                return
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
            randompick = random.randint(0, length - 1)
            
            # Add '.gif' to make it a proper gif, otherwise it will not load.
            link = sfwcategories[category][randompick]
            link = link + ".gif"
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Now go forth with sweet dreams and sweeter smiles.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="flowers")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def flowers(self, ctx, member: discord.Member=None):
        """ Give a member flowers and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "flowers"
        perform = "being given flowers by"
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you mentioned yourself. Please choose another.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            
            # Random number to pick a gif.
            if member_ult in guild.members:
                length = len(sfwcategories[category])
            else:
                return
            
            # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
            randompick = random.randint(0, length - 1)
            
            # Add '.gif' to make it a proper gif, otherwise it will not load.
            link = sfwcategories[category][randompick]
            link = link + ".gif"
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Enjoy your floral present, dear.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    

    
    
    
    # NOT SAFE FOR WORK
    
    @commands.command(name="bj")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bj(self, ctx, member: discord.Member=None):
        """ Blowjob a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "blowjob"
        hmtai = pyhmtai()

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                        f"{A} gives {B} a blowjob. Sloppy!",
                        f"{A} gives {B} the gawk gawk 8000!"
                       ]
            
            
            
            link = hmtai.nsfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="boobjob")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def boobjob(self, ctx, member: discord.Member=None):
        """ Boobjob a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "boobjob"
        hmtai = pyhmtai()

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                        f"{A} gives {B} a boobjob. Sticky!",
                        f"{B} gets the hottest boobjob from {A}."
                       ]
            
            
            
            link = hmtai.nsfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="handjob")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def handjob(self, ctx, member: discord.Member=None):
        """ Handjob a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "handjob"
        hmtai = pyhmtai()

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                        f"{A} gives {B} a handjob. Sticky!",
                        f"{B} gets a nice handjob from {A}."
                       ]
            
            
            
            link = hmtai.nsfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="footjob")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def footjob(self, ctx, member: discord.Member=None):
        """ Footjob a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "footjob"
        hmtai = pyhmtai()

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                        f"{A} gives {B} a footjob. Sticky!",
                        f"{B} gets a nice footjob from {A}."
                       ]
            
            
            
            link = hmtai.nsfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="creampie")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def creampie(self, ctx, member: discord.Member=None):
        """ Creampie a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "creampie"
        hmtai = pyhmtai()

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                        f"{A} gives {B} a drippy creampie. Sticky!",
                       ]
            
            
            
            link = hmtai.nsfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="dom")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def dom(self, ctx, member: discord.Member=None):
        """ Dom a member. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "femdom"
        hmtai = pyhmtai()

        clr = await ctx.embed_colour()
        

        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return
        
        # Check if the member is in the server:
        if member == None:
            if ctx.message.reference==None:
                member_ult = None
            elif ctx.message.reference.cached_message!=None:
                member_ult = ctx.message.reference.cached_message.author
            else:
                msg = await ctx.fetch_message(ctx.message.reference.message_id)
                member_ult = get(guild.members, id=msg.author.id)
        else:
            member_ult = member


        
        # If a member is not passed, send a message telling the user to mention or reply to a member. Otherwise, generates a random number and picks a gif from the list.     
        if member_ult == author:
            embed = discord.Embed(title="", description=f"Oh dear. You mentioned yourself. What a shame. Please mention someone else.", color=clr)
            await ctx.send(embed=embed)
        elif member_ult != None:
            if member_ult in guild.members:
                member = member_ult
            else:
                return
            A = f"{author.mention}"
            B = f"{member.mention}"
            action_list = [
                        f"{B} gets femdommed by {A}. Naughty!",
                       ]
            
            
            
            link = hmtai.nsfw(category)
            resp = requests.get(link)
            link = resp.json()
            link = link["url"]

            
            # Random number to pick an action.
            action_length = len(action_list)
            randomaction = random.randint(0,action_length-1)
            perform = action_list[randomaction]
            
            # Next we get the link and input it into the embed,
            embed = discord.Embed(title="", description=f"{perform}", color=clr)
            embed.set_image(url=link)
            
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"Oh dear. The person you mentioned isn't with us.", color=clr)
            await ctx.send(embed=embed)
    
    
    
    
    
    @commands.command(name="orgasm")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def orgasm(self, ctx):
        """ Cum. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "cum"
        hmtai = pyhmtai()
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return

        A = f"{author.mention}"
        action_list = [
                    f"{A} cums all over the place. Mommy chill!"
                ]

        link = hmtai.nsfw(category)
        resp = requests.get(link)
        link = resp.json()
        link = link["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="masturbate")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def masturbate(self, ctx):
        """ Masturbate. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "masturbation"
        hmtai = pyhmtai()
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return

        A = f"{author.mention}"
        action_list = [
                    f"{A} masturbates all over the place. Mommy chill!"
                ]

        link = hmtai.nsfw(category)
        resp = requests.get(link)
        link = resp.json()
        link = link["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="shlick")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def shlick(self, ctx):
        """ Shlick your pussy. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "pussy"
        hmtai = pyhmtai()
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return

        A = f"{author.mention}"
        action_list = [
                    f"{A} is playing with their wet pussy. Yum!"
                ]

        link = hmtai.nsfw(category)
        resp = requests.get(link)
        link = resp.json()
        link = link["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="panties")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def panties(self, ctx):
        """ Show your panties. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "pantsu"
        hmtai = pyhmtai()
        
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return
        if await self.config.guild(guild).enable_nsfw():
            if ctx.channel.nsfw == False:
                await ctx.send("This command is not allowed here. Go to an adult channel.")
                return
        else:
            await ctx.send("This command is not allowed.")
            return

        A = f"{author.mention}"
        action_list = [
                    f"{A} shows off their panties. Sexy!"
                ]

        link = hmtai.nsfw(category)
        resp = requests.get(link)
        link = resp.json()
        link = link["url"]
            
        # Random number to pick a gif.
        action_length = len(action_list)
        randomaction = random.randint(0,action_length-1)    
            
        perform = action_list[randomaction]
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{perform}", color=clr)
        embed.set_image(url=link)

            
        # Send the embed.
        await ctx.send(embed=embed)
    
    