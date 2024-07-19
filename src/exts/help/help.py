from discord import ApplicationContext, Bot, Cog, Embed, slash_command

from src.utils import getcatimageurl, mention_command
from src.utils.log import get_logger

log = get_logger(__name__)


class HelpCog(Cog):
    """Cog to provide help info for all available bot commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def help(self, ctx: ApplicationContext) -> None:
        """Shows help for all available commands."""
        embed = Embed(
            title="Help command",
            image=await getcatimageurl(),
        )
        embed.add_field(name=mention_command("ping", self.bot), value="sends a response with pong", inline=False)
        embed.add_field(name=mention_command("help", self.bot), value="gives a list of available commands for users")
        embed.add_field(name="", value="")
        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    """Register the HelpCog cog."""
    bot.add_cog(HelpCog(bot))
