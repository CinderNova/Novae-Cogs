from redbot.core.bot import Red
from .theatre import theatre

async def setup(bot: Red) -> None:
    await bot.add_cog(theatre(bot))
