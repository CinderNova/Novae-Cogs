import discord, json, random, datetime, asyncio
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from discord.utils import get
import redbot.core.data_manager
from typing import Callable, Optional
from ..abc import MixinMeta, CompositeMetaClass
from ..common.calc import Calculation
from ..common.pagination import Pagination

class Shop(MixinMeta):
    
    @commands.group(name="shop")
    @commands.guild_only()
    async def shop(self, ctx):
        
        """ Commands for the shop."""
    
    @shop.command()
    @commands.guild_only()
    async def overview(self, ctx):
        
        """Get an overview over what the shop offers, and its categories, as well as functionalities."""
        guild = ctx.guild
        embed = discord.Embed(title=f"**{guild.name}'s Shop Categories**", description="Below described are the categories the shop offers. Enjoy the sortiment.\n\nUse '''/viewshop (category)''' to view all the items listed in said category. \n\n", color=clr)
        embed.add_field(name="**Marriage Rings**", value="From Tier 1 to Tier 8.", inline=False)
        embed.add_field(name="**Houses**", value="From Level 1 to Level 5, \n```if you are married!```", inline=False)
        embed.add_field(name="**Pets**", value="From cats, dogs, to other pets one finds exotic, \n```if you are married!```", inline=False)
        embed.set_footer(text=f"{ts}")
        embed.set_image(url="attachment://Shop.png")
        await ctx.send(embed=embed)
    
         
    @shop.command()
    @commands.guild_only()
    async def buy(self, ctx, *, item: str):
        
        """Buy anything from the shop. Figure out what you want with ```shop overview```. Buy using the ID."""
        guild = ctx.guild
        id = str(guild.id)
        author = ctx.author
        with open(userslink, "r") as f:
            users= json.load(f)
        with open(economylink, "r") as f:
            economy = json.load(f)
        user = users["Servers"][id][str(author.id)]
        currency = await redbot.core.bank.get_currency_name(guild)
        rings = economy["Servers"][id]["Items"]["rings"]
        ring_1 = rings["ring_1"]
        ring_2 = rings["ring_2"]
        ring_3 = rings["ring_3"]
        ring_4 = rings["ring_4"]
        ring_5 = rings["ring_5"]
        ring_6 = rings["ring_6"]
        ring_7 = rings["ring_7"]
        ring_8 = rings["ring_8"]
        
        user = users["Servers"][id][str(author.id)]
        
        if item.lower() == "r01":
            if await redbot.core.bank.can_spend(author, ring_1["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_1["price"], currency, ring_1["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_1["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_1["name"], ts,ring_1["price"], currency, ring_1["tier"], ring_1["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 1"] +=1
                user["inventory"]["niu-rings"]["tiers"][0]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r02":
            if await redbot.core.bank.can_spend(author, ring_2["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_2["price"], currency, ring_2["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_2["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_2["name"], ts,ring_2["price"], currency, ring_2["tier"], ring_2["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 2"] +=1
                user["inventory"]["niu-rings"]["tiers"][1]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r03":
            if await redbot.core.bank.can_spend(author, ring_3["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_3["price"], currency, ring_3["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_3["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_3["name"], ts,ring_3["price"], currency, ring_3["tier"], ring_3["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 3"] +=1
                user["inventory"]["niu-rings"]["tiers"][2]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r04":
            if await redbot.core.bank.can_spend(author, ring_4["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_4["price"], currency, ring_4["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_4["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_4["name"], ts,ring_4["price"], currency, ring_4["tier"], ring_4["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 4"] +=1
                user["inventory"]["niu-rings"]["tiers"][3]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r05":
            if await redbot.core.bank.can_spend(author, ring_5["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_5["price"], currency, ring_5["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_5["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_5["name"], ts,ring_5["price"], currency, ring_5["tier"], ring_5["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 5"] +=1
                user["inventory"]["niu-rings"]["tiers"][4]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r06":
            if await redbot.core.bank.can_spend(author, ring_6["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_6["price"], currency, ring_6["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_6["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_6["name"], ts,ring_6["price"], currency, ring_6["tier"], ring_6["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 6"] +=1
                user["inventory"]["niu-rings"]["tiers"][5]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r07":
            if await redbot.core.bank.can_spend(author, ring_7["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_7["price"], currency, ring_7["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_7["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_7["name"], ts,ring_7["price"], currency, ring_7["tier"], ring_7["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 7"] +=1
                user["inventory"]["niu-rings"]["tiers"][6]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        elif item.lower() == "r08":
            if await redbot.core.bank.can_spend(author, ring_8["price"]) == False:
                await ctx.send("You need ```{:,} {}``` to buy the {}.".format(ring_8["price"], currency, ring_8["name"]))
            else:
                await redbot.core.bank.withdraw_credits(author, ring_8["price"])
                embed=discord.Embed(title="Purchase:", description="Purchase of {}: \n You have purchased this item. \n Date: {} \n ```Price: {:,} {}\nTier: {}\nID: {}```".format(ring_8["name"], ts,ring_8["price"], currency, ring_8["tier"], ring_8["id"]), color=clr)
                await ctx.send(embed=embed)
                user["inventory"]["niu-rings"]["tier 8"] +=1
                user["inventory"]["niu-rings"]["tiers"][7]+=1
                users["Servers"][id][str(author.id)] = user
                with open(userslink, "w") as f:
                    json.dump(users, f, indent=4)
        else:
            await ctx.send("Please enter a valid item ID from the shop!")
    
    @app_commands.command(description="View what the shop has to offer!")
    @app_commands.describe(category="Valid categories are houses, rings, pets.")
    @commands.guild_only()
    async def shopview(self, interaction: discord.Interaction, category: str):
        
        """View what the shop has to offer."""
        with open(economylink, "r") as f:
            economy = json.load(f)
        guild = interaction.guild
        id = str(guild.id)
        L = 5
        items = economy["Servers"][id]["Items"]
        rings = items["rings"]
        houses = items["houses"]
        pets = items["pets"]
        currencyname = await redbot.core.bank.get_currency_name(guild)
        
        
        keyword_r = ["rings", "ring", "marriage rings", "wedding rings", "bands", "marriage bands"]
        keyword_h = ["houses", "house", "mansion", "mansions", "living space", "villa", "villas"]
        keyword_p = ["pets", "pet", "animals", "animal"]        
        
        
        if category.lower() in keyword_r:
            items_list = []
            for key in rings:
                items_list.append(rings[key])
            async def get_page(page: int):
                embed = discord.Embed(title=f"**{guild.name}'s Shop**", description="Below is a showcase of our **Wedding Rings**. Enjoy the sortiment.\n\n", color=clr)
                offset = (page-1)*L
                for ring in items_list[offset: offset+L]:
                    embed.description += "```<<{}, Tier {}, ID: {}>>\n\nPrice:     {:,} {}```\n".format(ring['name'],ring['tier'],ring['id'], ring['price'],currencyname)
                embed.set_author(name=f"Requested by {interaction.user}")
                n = Pagination.compute_total_pages(len(items_list), L)
                embed.set_footer(text=f"Page {page} from {n}.              {ts}")
                return embed, n
            await Pagination(interaction, get_page).navegate()
            
        elif category.lower() in keyword_h:
            items_list = []
            for key in houses:
                items_list.append(houses[key])
            async def get_page(page: int):
                embed = discord.Embed(title=f"**{guild.name}'s Shop**", description="Below is a showcase of our **Houses**. Enjoy the sortiment. Only available for those that are married.\n\n", color=clr)
                offset = (page-1)*L
                for house in items_list[offset: offset+L]:
                    embed.description += "```<<{}, Level {}, ID: {}>>\n\nPrice:     {:,} {}```\n".format(house['name'],house['level'],house['id'],house['price'],currencyname)
                embed.set_author(name=f"Requested by {interaction.user}")
                n = Pagination.compute_total_pages(len(items_list), L)
                embed.set_footer(text=f"Page {page} from {n}.              {ts}")
                return embed, n
            await Pagination(interaction, get_page).navegate()
        elif category.lower() in keyword_p:
            items_list = []
            for key in pets:
                items_list.append(pets[key])
            async def get_page(page: int):
                embed = discord.Embed(title=f"**{guild.name}'s Shop**", description="Below is a showcase of our **Pets**. Enjoy the sortiment. Only available for those that are married.\n\n", color=clr)
                offset = (page-1)*L
                for pet in items_list[offset: offset+L]:
                    for key in pet:
                            embed.description += "```<<{}>>\n\nPrice:     {:,} {}```\n".format(key,pet[key],currencyname)
                embed.set_author(name=f"Requested by {interaction.user}")
                n = Pagination.compute_total_pages(len(items_list), L)
                embed.set_footer(text=f"Page {page} from {n}.              {ts}")
                return embed, n
            await Pagination(interaction, get_page).navegate()
        else:
            await interaction.response.send_message("Please enter a category.", ephemeral=True)
        
    
    