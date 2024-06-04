from redbot.core.bot import Red
from .confession import confession

async def setup(bot: Red) -> None:
    await bot.add_cog(confession(bot))
