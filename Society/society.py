import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager
from typing import Callable, Optional
from .abc import MixinMeta, CompositeMetaClass
from .common.calc import Calculation
from .common.pagination import Pagination
from .core.custom import Customcommands
from .core.economy import Economy
from .core.jobs import Jobs
from .core.marriage import Marriage
from .core.settings import Settings 
from .core.shop import Shop



# Set the timestamp as of the time of the command.
ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

clr=0x690615  

    



default_inventory = {
                    "rings" : {
                    "tier 1" : 0,
                    "tier 2" : 0,
                    "tier 3" : 0,
                    "tier 4" : 0,
                    "tier 5" : 0,
                    "in_use" : [0, 0, 0, 0, 0]
                   },
                    "houses" : {
                    "tier 1" : 0,
                    "tier 2" : 0,
                    "tier 3" : 0,
                    "tier 4" : 0,
                    "tier 5" : 0,
                    "in_use" : [0,0,0,0,0]
                   },
                    "items" : {  
                    },
                    "max_rings" : 10,
                    "max_houses" : 5,
                    "space_filled" : 0,
                },



class society(commands.Cog, Calculation, Pagination, Customcommands, Economy, Jobs, Marriage, Shop, Settings,metaclass = CompositeMetaClass):
    
    """
    Society Cog.
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/debug.log"
        self.debug_file = None
        self.identifier = self.bot.user.id

        self.config = Config.get_conf(self, identifier = self.identifier, force_registration=True)
        default_guild = {
            'enable_debug' : False,
            'enable_gambling' : True,
            'enable_bonuses' : True,
            'enable_jobs' : True,
            'enable_marriage' : True,
            'enable_shop' : True,
            
            'default_income' : 5000,
            'max_bet' : 50000,
            
            'users' : {},
            
            'jobs' : {
                    "queen" : ["queen", "good", 5000, 1],
                    "king" : ["king", "good", 5000, 1],
                    "knight" : ["knight", "good", 5000, 1],
                    "jester" : ["jester", "neutral", 5000, 2],
                    "pawn" : ["pawn", "neutral", 5000, 2],
                    "servant" : ["servant", "neutral", 5000, 2],
                    "mafioso" : ["mafioso", "bad", 5000, 3],
                    "prostitute" : ["prostitute", "bad", 5000, 3],
                    "bishop" : ["bishop", "bad", 5000, 3]
                },
            
            'job_bonuses' : {
                "first" : 1.00,
                "second" : 1.25,
                "third" : 1.375},
            
            'crime_messages' : {"W" : 
                [   "You robbed someone and stole their watch. Easy money!",
                    "The dollar store that you stole from was jacked!",
                    "Robbing a grandma is pretty low, but pays...",
                    "Lucky you! There was a diamond ring on the woman you stole from.",
                    "The blackmarket deal you had going on sold without an issue, easy bread."
                    ],
                                "L" : 
                [   "While doing drugs, you were caught, and fined.",
                    "You were caught mining crypto. You now have to pay the electricity bill.",
                    "Whoever you tried to steal from, knocked the shit out of you, and robbed you instead.",
                    "A muscle mommy you tried to kidnap, instead, knocked you out and sold your kidney. Now you have to pay for a new one."
                    ]
                },
            
            'shopmenu' : 
                {
            'houses' : {
                },
            
            'rings' : {
                },
            
            'pets' : {
                },
            
            'custom_items' : {
                }, 
            }
        }
        self.config.register_guild(**default_guild)
        default_user = {
            "inventory" : default_inventory,
            "income" : 0,
            "jobs" : {
                "job_one" : {
                    "last_worked" : "",
                    "name" : ""
                    },
                "job_two" : {
                    "last_worked" : "",
                    "name" : ""
                    },
                "job_three" : {
                    "last_worked" : "",
                    "name" : ""
                    },
                "extra_job" : {
                    "last_worked" : "",
                    "name" : ""
                    },
            },
            "marriages" : {},
            "pets" : {},
            "specialties" : {},
            "level" : 1
        }
        self.config.register_user(**default_user)
        
    async def debug_log(self, guild, command, message):
        current_directory = redbot.core.data_manager.cog_data_path(cog_instance=self)
        debug_file_path = f"{current_directory}/{guild.id}-debug.log"
        debug_file = open(debug_file_path, 'a') 
        debug_file.write(f"{datetime.datetime.now()} - Command '{command}': {message}\n")
        debug_file.close()    
        
    async def create_shopitem(self, ctx, new_name : str, new_price : int, new_level: int, itemtype: str, new_requirement, *, comment: str):
        guild = ctx.guild
        
        shopmenu = await self.config.guild(guild).shopmenu()
        if itemtype.lower() in ['house', 'houses']:
            itemtype = "houses"
            length = len(shopmenu['houses'].items())
            obj = {
            "name" : new_name,
            "object" : itemtype,
            "level" : new_level,
            "number" : length,
            "price" : new_price,
            "requirement" : new_requirement,
            'comment' : None
            }
            shopmenu['houses'][f'{length}'] = obj
            await self.config.guild(guild).shopmenu.set(shopmenu)
        elif itemtype.lower() in ['rings', 'ring']:
            itemtype = "rings"
            length = len(shopmenu['rings'].items())
            obj = {
            "name" : new_name,
            "object" : itemtype,
            "level" : new_level,
            "number" : length,
            "price" : new_price,
            "requirement" : new_requirement,
            'comment' : None
            }
            shopmenu['rings'][f'{length}'] = obj
            await self.config.guild(guild).shopmenu.set(shopmenu)
        elif itemtype.lower() in ['pets', 'pet']:
            itemtype = "pets"
            length = len(shopmenu['pets'].items())
            obj = {
            "name" : new_name,
            "object" : itemtype,
            "level" : new_level,
            "number" : length,
            "price" : new_price,
            "requirement" : new_requirement,
            'comment' : None
            }
            shopmenu['pets'][f'{length}'] = obj
            await self.config.guild(guild).shopmenu.set(shopmenu)
        elif itemtype.lower() in ['custom']:
            length = len(shopmenu['custom_items'].items())
            obj = {
            "name" : new_name,
            "object" : itemtype,
            "level" : new_level,
            "number" : length,
            "price" : new_price,
            "requirement" : new_requirement,
            'comment' : None
            }
            shopmenu['custom_items'][f'{length}'] = obj
            await self.config.guild(guild).shopmenu.set(shopmenu)
        else:
            return "Error"
    

    async def create_job(new_name: str, new_income: int, new_orientation: str):
        obj = {
            
        }
    

        """ Custom Shit. """
    
    
    @commands.command()
    @commands.guild_only()
    async def inventory(self, ctx):
        
        """Show your inventory."""
        
        guild = ctx.guild
        id = str(guild.id)
        author = ctx.author
        with open(userslink, "r") as f:
            users= json.load(f)
        with open(economylink, "r") as f:
            economy = json.load(f)
        user = users["Servers"][id][str(author.id)]
        houses = economy["Servers"][id]["Items"]["houses"]
        rings = economy["Servers"][id]["Items"]["rings"]
        ring_1 = rings["ring_1"]
        ring_2 = rings["ring_2"]
        ring_3 = rings["ring_3"]
        ring_4 = rings["ring_4"]
        ring_5 = rings["ring_5"]
        ring_6 = rings["ring_6"]
        ring_7 = rings["ring_7"]
        ring_8 = rings["ring_8"]
        
        house_1 = houses["house_1"]
        house_2 = houses["house_2"]
        house_3 = houses["house_3"]
        house_4 = houses["house_4"]
        house_5 = houses["house_5"]
        
        
        user = users["Servers"][id][str(author.id)]
        userinv = user["inventory"]
        userrings_niu = userinv["niu-rings"]
        userrings_iu = userinv["iu-rings"]
        userhouses_iu = userinv["iu-houses"]
        
        niu_vec = userrings_niu["tiers"]
        iu_vec = userrings_iu["tiers"]
        houseiu_vec = userhouses_iu
        G = "Below is your inventory listed. \nDate: {}\n**# Rings**```Not in Use: \n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n```".format(ts, 
                                                                                                                                                ring_1["name"], userrings_niu["tier 1"], ring_1["tier"], ring_1["id"],
                                                                                                                                                ring_2["name"], userrings_niu["tier 2"], ring_2["tier"], ring_2["id"],
                                                                                                                                                ring_3["name"], userrings_niu["tier 3"], ring_3["tier"], ring_3["id"],
                                                                                                                                                ring_4["name"], userrings_niu["tier 4"], ring_4["tier"], ring_4["id"],
                                                                                                                                                ring_5["name"], userrings_niu["tier 5"], ring_5["tier"], ring_5["id"],
                                                                                                                                                ring_6["name"], userrings_niu["tier 6"], ring_6["tier"], ring_6["id"],
                                                                                                                                                ring_7["name"], userrings_niu["tier 7"], ring_7["tier"], ring_7["id"],
                                                                                                                                                ring_8["name"], userrings_niu["tier 8"], ring_8["tier"], ring_8["id"]
        )
        H = "\n```In Use: \n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n```".format( 
                                                                                                                                                ring_1["name"], userrings_iu["tier 1"], ring_1["tier"], ring_1["id"],
                                                                                                                                                ring_2["name"], userrings_iu["tier 2"], ring_2["tier"], ring_2["id"],
                                                                                                                                                ring_3["name"], userrings_iu["tier 3"], ring_3["tier"], ring_3["id"],
                                                                                                                                                ring_4["name"], userrings_iu["tier 4"], ring_4["tier"], ring_4["id"],
                                                                                                                                                ring_5["name"], userrings_iu["tier 5"], ring_5["tier"], ring_5["id"],
                                                                                                                                                ring_6["name"], userrings_iu["tier 6"], ring_6["tier"], ring_6["id"],
                                                                                                                                                ring_7["name"], userrings_iu["tier 7"], ring_7["tier"], ring_7["id"],
                                                                                                                                                ring_8["name"], userrings_iu["tier 8"], ring_8["tier"], ring_8["id"])
        J = "\n**# Houses**\n```In Use:\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}\n\n{}: {} \n- Tier {}, ID: {}```".format(
            house_1["name"], houseiu_vec[0], house_1["level"], house_1["id"],
            house_2["name"], houseiu_vec[1], house_2["level"], house_2["id"],
            house_3["name"], houseiu_vec[2], house_3["level"], house_3["id"],
            house_4["name"], houseiu_vec[3], house_4["level"], house_4["id"],
            house_5["name"], houseiu_vec[4], house_5["level"], house_5["id"]
        )
        embed = discord.Embed(title="**User Inventory**", description=f"User: {author.mention}\n\n"+G+H+J, color=clr)
        await ctx.send(embed=embed)
        
    
    
        
 
    
    
    
    
    
    
    