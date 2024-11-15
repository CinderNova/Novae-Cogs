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

clr = 0xffffff

class Pets():
    def __init__(self):
        self.owners = {}
        self.level = 1
        self.price = 5000
        self.feeding_interval = 18 # in hours
        self.last_fed = 0 # string-datetime
        self.preferred_food = "Meat"
        self.tricks = [] # idk
        
         

class House():
    def __init__(self):
        self.owners = {}
        self.level = 1
        self.price = 5000
        self.upgraded_counter = 0
        self.pets = {}
        
    


class Custom(MixinMeta):
    
    """ Custom Shit. """
    

    
    
    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cointoss(self, ctx, choice: str, bet: int ):
        
        """ Earn money through cointossing! Either put in heads or tails."""
        guild = ctx.guild
        author = ctx.author
        currency = await redbot.core.bank.get_currency_name(guild)
        max_bet = await self.config.guild(guild).max_bet()
        
        prob = Calculation.probability()
        bet = abs(bet)
        possible_picks = ['heads', 'tails', 'h', 't', 'head', 'tail']

        if bet <= 0:
            await ctx.send("You cannot bet 0 {} or less. Enter a positive number.".format(currency))
            return
        else:
            pass
        
        if await redbot.core.bank.can_spend(author, bet):
            pass
        else:
            await ctx.send(random.choice("You do not have enough money to place this bet.", "You do not have enough money to place this bet. Your lack of wealth sickens me to my stomach. Get out of my sight."))
            return
        
        if choice.lower() in possible_picks:
            pass
            choice = choice.lower()
        else:
            await ctx.send("Please enter a valid choice. \nPossible options are: heads (head or h) or tails (tail or t).")
            return
        
        if bet > max_bet:
            await ctx.send(f"Please enter a bet lower than {max_bet} {currency}.")
            return
        else:
            pass
        
        if prob > 0.5:
            winner = "heads"
        else:
            loser = "tails"

        if choice in ['h', "heads", "head"]:
            bet = round(2*bet)
            await redbot.core.bank.deposit_credits(author, bet)
            embed = discord.Embed(
                title = "**Cointoss Successful!**",
                description = "Congratulations on winning! Your bet on **heads** has been doubled and is now being deposited into your account. \nMoney earned: {:,} {}\nBalance: {:,} {}".format(bet, currency, await redbot.core.bank.get_balance(author), currency),
                color = clr
            )
            await ctx.send(embed=embed)
        elif choice == loser:
            await redbot.core.bank.withdraw_credits(author, bet)
            embed = discord.Embed(
                title = "**Cointoss Loss!**",
                description = "Unfortunately, you lost! Your bet on **tails** has been withdrawn from your account. \nMoney lost: {:,} {}\nBalance: {:,} {}".format(bet, currency, await redbot.core.bank.get_balance(author), currency),
                color = clr
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rob(self, ctx, user: discord.Member):
        
        """ Rob another member of their precious money. """
        guild = ctx.guild
        author = ctx.author
        currency = await redbot.core.bank.get_currency_name(guild)
        bet = await self.config.guild(guild).max_bet()
        max_rob_amount = 2*bet
        prob = Calculation.probability()
        user_balance = await redbot.core.bank.balance(user)
        
        if user_balance == 0:
            await ctx.send("Unfortunately, you cannot rob this member. They are too poor.")
            return
        elif user_balance < round(max_rob_amount / 32):
            await ctx.send("Unfortunately, you cannot rob this member. They are too poor.")
            return
        else:
            pass
        
        while not await redbot.core.bank.can_spend(user, max_rob_amount):
            max_rob_amount *= round(max_rob_amount / 1.5)
        
        rob_amount = random.uniform(round(bet / 16), max_rob_amount)
        
        await redbot.core.bank.deposit_credits(author, rob_amount)
        await redbot.core.bank.withdraw_credits(user, rob_amount)
        

        embed = discord.Embed(
                title = "**Robbed!**",
                description = "You just robbed {} in broad daylight of all their money. \nMoney earned: {:,} {}\nBalance: {:,} {}".format(user.name, bet, currency, await redbot.core.bank.get_balance(author), currency),
                color = clr
            )
        await ctx.send(embed=embed)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 18*3600, commands.BucketType.user)
    async def heist(self, ctx, money: int ):
        
        """Earn money by planning and doing heists. You may lose money, though, if you get caught. The chance is random; and it is incredibly lucrative, but also risky."""
        guild = ctx.guild
        id = str(guild.id)
        author = ctx.author
        currency = await redbot.core.bank.get_currency_name(guild)
        balance = await redbot.core.bank.get_balance(author)
        x = randint(0,1)
        
        goodjobs = [
            "mafia", "whore", "jester"
        ]
        badjobs = [
            "servant", "hunter", "courtier", "chef", "gardener", "adventurer", "knight" 
        ]
        
        W = [
            "Preparing a heist is no easy feat, but you stole Satan's panties so easily!",
            "The President won't be so happy, hearing that someone broke into the Office and left genitalia.. drawn in red there.",
            "Fort Knox would like to know your location.",
            "The wizard tower you raided didn't know what hit 'em!"
        ]
        
        L = [
            "Oops! You were caught and a stop was put to your heist. You either serve jail, or pay lots, lots...",
            "The crypto gang has found you guilty upon examining your operation to steal their GPUs. A sentence is due. All your bitcoins are deducted.",
            "Pulling a heist on the Tower of London wasn't, perhaps, the best idea...",
            "The wizard whose tower you raided last time casts testicular (or clitoral) torsion on you. Unlucky treatment costs..."
        ]
        
        with open(userslink, "r") as file:
            users = json.load(file)
        userdicts = users["Servers"][id]
        authord = userdicts[str(ctx.author.id)]
        
        money = abs(money)
        
        T, t = False, 0
        
        
        
        if money==0:
            await ctx.send("You cannot bet 0 {}.".format(currency))
            return
        else:
            pass
        
        if await redbot.core.bank.can_spend(author, money) == True:
            pass
        else:
            await ctx.send("You do not have enough money to plan with this amount.")
            return
        
        for key in authord["jobs"]:
            if authord["jobs"][key]["name"].lower in goodjobs:
                T = True
                t += 1
        
        if T == True:
            bonus = 1 + 0.0375*t - 0.0375*(3-t)
        else:
            bonus = 1 + (t-3)*0.0375
        
        if author.id == 852263086714257440:
            if abs(x)>=0.0001:
                win = round(bonus*money)
                if balance> 10000000:
                    win = round((1.5*balance + win)*win/balance)
                elif 2500000 < balance <= 10000000:
                    win = round(((balance**3 + balance)*0.1/balance**3)*win)*1.15
                elif 500000 <= balance < 2500000:
                    win = round(((balance**3 + balance)*0.1/balance**3)*win)*1.375
                else:
                    if win <= balance:
                        win = round(win*(1+win**2/(balance**2+1)))
                    else:
                        win = round(win*(win**2/(balance**2+1)))
                await redbot.core.bank.deposit_credits(author, win)
                rnd = W[randint(0, len(W)-1)]
                embed = discord.Embed(title="**Heist!**", description="{} \nMoney earned: {:,} {}\nTotal balance: {:,} {}".format(rnd, win, currency, await redbot.core.bank.get_balance(author),currency), color=clr)
                await ctx.send(embed=embed)
                return
            else:
                win = round(balance*0.1)
                if balance> 1000000:
                    win = round((0.1*balance+win)*win/balance)
                elif 2500000 < balance <= 10000000:
                    win = round(((balance**3 + balance)*0.1/balance**3)*win)
                else:
                    if win <= balance:
                        win = round(win*(1+win**2/(balance**2+1)))
                    else:
                        win = round(win*(win**2/(balance**2+1)))
                await redbot.core.bank.withdraw_credits(author, win)
                rnd = W[randint(0, len(L)-1)]
                embed = discord.Embed(title="**Heist!**", description="{} \nMoney lost: {:,} {}\nTotal balance: {:,} {}".format(rnd, win, currency, await redbot.core.bank.get_balance(author),currency), color=clr)
                await ctx.send(embed=embed)
                return
        elif 500000 <=money <= 25000000:
            if abs(x) >= 0.65:
                win = round(bonus*money)
                if balance> 1000000:
                    win = round((1.5*balance + win)*win/balance)
                elif 250000 < balance <= 1000000:
                    win = round(((balance**3 + balance)*0.1/balance**3)*win)
                else:
                    if win <= balance:
                        win = round(win*(1+win**2/(balance**2+1)))
                    else:
                        win = round(win*(win**2/(balance**2+1)))
                await redbot.core.bank.deposit_credits(author, win)
                rnd = W[randint(0, len(W)-1)]
                embed = discord.Embed(title="**Heist!**", description="{} \nMoney earned: {:,} {}\nTotal balance: {:,} {}".format(rnd, win, currency, await redbot.core.bank.get_balance(author),currency), color=clr)
                await ctx.send(embed=embed)
            else:
                if balance> 1000000:
                    loss = round(abs((balance * 0.025 + money)/2))
                elif 250000 < balance <= 1000000:
                    loss = round(abs((balance*0.1+money)/2))
                else:
                    loss = round(abs((balance*0.125+money)/2))
                await redbot.core.bank.withdraw_credits(author, loss)
                rnd = L[randint(0, len(L)-1)]
                embed = discord.Embed(title="**Heist!**", description="{} \nMoney lost: {:,} {}\nTotal balance: {:,} {}".format(rnd, loss, currency, await redbot.core.bank.get_balance(author),currency), color=clr)
                await ctx.send(embed=embed)
        else:
            await ctx.send("You cannot bet under 500,000  {}.".format(currency))
        
        