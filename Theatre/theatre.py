import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager

# Set the timestamp as of the time of the command.
timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
giflist = "/home/Themis/cogs/CogManager/cogs/theatre/cmdgifs.json"

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
    
    @commands.command(name="hug")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def hug(self, ctx, member: discord.Member=None):
        """ Hug a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "hug"
        perform = "being hugged by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. A hug a day keeps the doctor away!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
            
    @commands.command(name="cuddle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cuddle(self, ctx, member: discord.Member=None):
        """ Cuddle a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "cuddle"
        perform = "being cuddled by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Is it not the best to cuddle?", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="snuggle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def snuggle(self, ctx, member: discord.Member=None):
        """ Snuggle a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "snuggle"
        perform = "being snuggled by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Share the joy and snuggle each other!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="nuzzle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def nuzzle(self, ctx, member: discord.Member=None):
        """ Nuzzle a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "nuzzle"
        perform = "being nuzzled by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Someone as wonderful as you.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="comfort")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def comfort(self, ctx, member: discord.Member=None):
        """ Comfort a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "comfort"
        perform = "being comforted by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. They are there for you.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="kiss")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def kiss(self, ctx, member: discord.Member=None):
        """ Kiss a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "kiss"
        perform = "being kissed by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Such an intimate embrace indeed!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="yurihug")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def yurihug(self, ctx, member: discord.Member=None):
        """ Yurihug a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "yurihug"
        perform = "being yurihugged by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Hugs are the best.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="yuricuddle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def yuricuddle(self, ctx, member: discord.Member=None):
        """ Yurihug a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "yuricuddle"
        perform = "being yuricuddled by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}, so adorable!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="yurisnuggle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def yurisnuggle(self, ctx, member: discord.Member=None):
        """ Yurisnuggle a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "yurisnuggle"
        perform = "being yurisnuggled by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. I spy two people snuggling!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="yurikiss")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def yurikiss(self, ctx, member: discord.Member=None):
        """ Yurihug a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "yurikiss"
        perform = "being yurikissed by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Hold on, that is so gay.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="bite")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bite(self, ctx, member: discord.Member=None):
        """ Bite a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "bite"
        perform = "being bitten by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Reminder that you shall only bite with consent, my dears.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="pat")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member=None):
        """ Pat a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "pat"
        perform = "being pat by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Are you not so cute?", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
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
    
    @commands.command(name="lick")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def lick(self, ctx, member: discord.Member=None):
        """ Lick a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "lick"
        perform = "being licked by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. How tasty one can be..", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="love")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def love(self, ctx, member: discord.Member=None):
        """ Love a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "love"
        perform = "being loved by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Everyone is loved, and you especially by {author.name}.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="poke")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def poke(self, ctx, member: discord.Member=None):
        """ Bite a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "poke"
        perform = "being poked by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Is anyone there? No?", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="bully")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bully(self, ctx, member: discord.Member=None):
        """ Bully a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "bully"
        perform = "being bullied by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Who was bad? You were!", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="cap")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cap(self, ctx, member: discord.Member=None):
        """ Bite a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "cap"
        perform = "being capped by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Keep calm and cope.", color=clr)
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
    
    @commands.command(name="destroy")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def destroy(self, ctx, member: discord.Member=None):
        """ Destroy a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "destroy"
        perform = "being destroyed by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Nothing was left of them following that day..", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="bonk")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def bonk(self, ctx, member: discord.Member=None):
        """ Bonk a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "bonk"
        perform = "being bonked by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Bonk, go to jail.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="tickle")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def tickle(self, ctx, member: discord.Member=None):
        """ Tickle a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "tickle"
        perform = "being tickled by"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. Is someone ticklish? I hope not!", color=clr)
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
    
    @commands.command(name="handhold")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def handhold(self, ctx, member: discord.Member=None):
        """ Hold the hand of a member and interact with them. You can either mention them (and leave it empty) or tag them. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "handhold"
        perform = "is holding hands with"
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
            embed = discord.Embed(title="", description=f"{member_ult.mention} is {perform} {author.mention}. What a sweet display of affection.", color=clr)
            embed.set_image(url=link)
            
            # Send the embed.
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description=f"My apologies, {author.name}. \n I was not able to fulfill your command, as you have not mentioned or replied to a member of our establishment.", color=clr)
            await ctx.send(embed=embed)
    
    @commands.command(name="blush")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def blush(self, ctx):
        """ Blush and act shy. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "blush"
        perform = "is blushing."
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        

        length = len(sfwcategories[category])

            
        # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
        randompick = random.randint(0, length - 1)
            
        # Add '.gif' to make it a proper gif, otherwise it will not load.
        link = sfwcategories[category][randompick]
        link = link + ".gif"
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{author.mention} {perform}. Come here, darling.", color=clr)
        embed.set_image(url=link)
            
        # Send the embed.
        await ctx.send(embed=embed)

    @commands.command(name="run")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def run(self, ctx):
        """ Run away and act shy. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "run"
        perform = "is running away."
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        

        length = len(sfwcategories[category])

            
        # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
        randompick = random.randint(0, length - 1)
            
        # Add '.gif' to make it a proper gif, otherwise it will not load.
        link = sfwcategories[category][randompick]
        link = link + ".gif"
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{author.mention} {perform}. Why the hurry, sweetie?", color=clr)
        embed.set_image(url=link)
            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="hide")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def hide(self, ctx):
        """ Hide and act shy. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "hide"
        perform = "is hiding."
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        

        length = len(sfwcategories[category])

            
        # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
        randompick = random.randint(0, length - 1)
            
        # Add '.gif' to make it a proper gif, otherwise it will not load.
        link = sfwcategories[category][randompick]
        link = link + ".gif"
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{author.mention} {perform}. What is the matter, precious?", color=clr)
        embed.set_image(url=link)
            
        # Send the embed.
        await ctx.send(embed=embed)
    
    @commands.command(name="cry")
    @commands.guild_only()   
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cry(self, ctx):
        """ Cry. """
        
        # Basic checks.
        guild = ctx.guild
        author = ctx.message.author
        category = "cry"
        perform = "is crying."
        clr = await ctx.embed_colour()
        
        # Debug Statement
        if await self.config.guild(guild).enable_debug():
            await self.debug_log(guild, category, "Running " + category + " command of 'theatre' cog.")
            return
        
        if await self.config.guild(guild).enable_blacklist():
            if ctx.channel.id in await self.config.guild(guild).channel_blacklist():
                await ctx.send("This command is not allowed here.")
                return

        # Load the file of gif links into a dict.
        with open(giflist, "r") as file:
            gifdict = json.load(file)
            
        # Access the key:value pair of key 'links' associated with the value, 'list of dictionaries (categories) for actions'.
        gifcategories = gifdict["links"]
        
        # Access the sfw categories (at list index 0, nsfw are at list index 1).
        sfwcategories = gifcategories[0]
        

        length = len(sfwcategories[category])

            
        # 'length - 1' because of how python assigns values to vectors / lists, they start at zero.    
        randompick = random.randint(0, length - 1)
            
        # Add '.gif' to make it a proper gif, otherwise it will not load.
        link = sfwcategories[category][randompick]
        link = link + ".gif"
            
        # Next we get the link and input it into the embed,
        embed = discord.Embed(title="", description=f"{author.mention} {perform}. Do you need to be consoled?", color=clr)
        embed.set_image(url=link)
            
        # Send the embed.
        await ctx.send(embed=embed)
    
    
    
    
    
    
    
    
    
    
    