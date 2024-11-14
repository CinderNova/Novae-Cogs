Here is a bit of code documentation.

**Used packages:**
asyncio, random, discordpy, datetime, redbot

**redbot datamanager:** https://docs.discord.red/en/stable/framework_datamanager.html
**redbot config:** https://docs.discord.red/en/stable/framework_config.html
**redbot bank:** https://docs.discord.red/en/stable/framework_bank.html
**redbot LevelUp** (access user levels): 
#      levelup = self.bot.get_cog("LevelUp")
#      levelconfig = levelup.get_conf(ctx.guild)
#      profile = levelconfig.get_profile(user_id)
#      level: int = profile.level

**Pythonic:**
- Instead of "if elif elif .... else", "match ... case" works too. Example: https://peps.python.org/pep-0636/
- [item for item in LIST if ...] is the same as "prev = [], for item in LIST: prev.append(item)". It's preferable since it shortens code a lot
- Datetime: i wrote a function for determining the amount of hours that passed between two points in time t1, t2. in /common.calc.py



**General Goals**:
- Enable / disable features, can be found in /core.settings.py, in particular: gambling, jobs, bonuses, marriage, shop, debug
- Set certain default numbers, found in /core.settings.py, in particular: default job income, the max_bet
- Add / remove / change jobs. Jobs have 4 qualities: their income (the max income they can generate, can vary between jobs), their alignment (i.e. queen / king is good, mafioso bad, ...), and their tier (i.e. some are tier 1 < tier 2 < tier 3, yielding higher income (with a bonus)).
- Change / reset job bonuses. Found in /core.settings.py. Default is 1: 1.00, 2: 1.25, 3: 1.375.
- Add / remove / change messages for heists, robbing
- Add / remove / change items for the shop
- Add view shop
- Add "buy" command
- Add "inventory" command that shows level, username, money, inventory
- Add "marry" command to propose to someone
- Add "marriages" command that shows your marriages (including houses, rings, ...)
- Add "divorce" command
- Add cookies and flowers. Flowers need to be grown (some random amount of times) and there is a set cooldown for each watering until they are grown fully, before they can be given to someone else. Both are one-time use
- Pets need to be fed regularly (use the datetime function I made). Rings and houses are mainly for marriage, will be implemented later
- Add marriage feature

