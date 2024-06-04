from redbot.core.bot import Red
from .overseer import overseer

async def setup(bot: Red) -> None:
    await bot.add_cog(overseer(bot))
