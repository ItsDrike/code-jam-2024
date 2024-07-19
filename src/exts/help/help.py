from discord import ApplicationContext, Bot, Cog, slash_command

from src.utils.log import get_logger

log = get_logger(__name__)


class HelpCog(Cog):
    """Cog to verify the bot is working."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def help(self, ctx: ApplicationContext) -> None:
        """Help command shows available commands."""
        await ctx.respond("hello")


def setup(bot: Bot) -> None:
    """Register the HelpCog cog."""
    bot.add_cog(HelpCog(bot))
