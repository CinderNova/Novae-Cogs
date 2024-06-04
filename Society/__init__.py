from redbot.core.bot import Red
from .society import society

async def setup(bot: Red) -> None:
    await bot.add_cog(society(bot))
