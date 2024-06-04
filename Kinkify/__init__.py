from redbot.core.bot import Red
from .kinkify import kinkify

async def setup(bot: Red) -> None:
    await bot.add_cog(kinkify(bot))
