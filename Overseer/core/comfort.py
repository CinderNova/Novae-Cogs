import discord, json, random, asyncio, logging, traceback, redbot.core.data_manager, datetime, re
from redbot.core import commands, app_commands, utils
from redbot.core.bot import Red
from redbot.core.config import Config
from datetime import timedelta
from discord.utils import get

from ..abc import MixinMeta, CompositeMetaClass
from .settings import Settings

class Comfort(MixinMeta):
    
    """
    Moderation Commands / Methods.
    """
    
    @app_commands.command(description="Change or request a custom role for boosting.")
    @app_commands.guild_only()
    @app_commands.describe(custom_name="Enter a valid name for the role!", custom_colour="Enter a valid hex code (format: #000000 as example).")
    async def boosting_role(self, interaction: discord.Interaction, custom_name: str, custom_colour: str):

        """ Create or manage a boosting role. """
        
        member = interaction.user
        guild = interaction.guild
        boost_list = await self.config.guild(guild).boosting_users()
        boost_role = get(guild.roles,id= await self.config.guild(guild).booster_role())
        toprole = get(guild.roles, id= await self.config.guild(guild).top_role())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        is_in = False
        
        if boost_role == None:
            return
        
        if len(custom_colour) > 7:
            await interaction.response.send_message(f"Please enter a valid hex colour code (format #000000).", ephemeral=True)
            return
        else:
            if custom_colour[0] == "#" or custom_colour[:6] == '0x' :
                custom_colour = discord.Colour.from_str(custom_colour)
            else:
                await interaction.response.send_message(f"Please enter a valid hex colour code (format #000000).", ephemeral=True)
                return
        
        if boost_role in member.roles:
            
            if boost_list != {}:
                for keys in boost_list:
                    if boost_list[keys]["user_id"] == member.id:
                        is_in = True
                        memberlog = boost_list[keys]
            else:
                memberlog = None
                    
            try:
                oldrole = get(guild.roles, id = memberlog["custom_role"])
            except:
                oldrole = None
            
            if is_in == False or oldrole == None:
                
                customrole = await guild.create_role(name=custom_name, colour=custom_colour)
                await customrole.edit(position=toprole.position)    
                boost_list[member.id] = {
                    "user_id" : member.id,
                    "user_name" : member.name,
                    "date" : timestamp,
                    "custom_role" : customrole.id,
                    "custom_colour" : f"{str(custom_colour)}",
                    "custom_name" : custom_name
                    }
                await member.add_roles(customrole)
                    
                await self.config.guild(guild).boosting_users.set(boost_list)
                await interaction.response.send_message(f"Your role has been created: {customrole.mention}", ephemeral=True)
            
            else:
                        
                await oldrole.edit(name=custom_name, colour = custom_colour, position = toprole.position - 1)
                memberlog["custom_colour"] = f"{str(custom_colour)}"
                memberlog["custom_name"] = custom_name
                boost_list[member.id] = memberlog
                await member.add_roles(oldrole)
                        
                await self.config.guild(guild).boosting_users.set(boost_list)
                await interaction.response.send_message(f"Your role has been changed: {oldrole.mention}", ephemeral=True)

                
        else:
            await interaction.response.send_message(f"You have not boosted the server yet. Boost the server to request or change your custom role.", ephemeral=True)
        
        
        
        
    