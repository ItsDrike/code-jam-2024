import discord
from discord import ApplicationContext, Bot, CheckFailure, Cog, SlashCommand, SlashCommandGroup, slash_command
from discord.ext.commands import CheckFailure as CommandCheckFailure
from discord.ext.pages import Page, Paginator

from src.utils import mention_command
from src.utils.log import get_logger

log = get_logger(__name__)


class HelpCog(Cog):
    """Cog to provide help info for all available bot commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def help(self, ctx: ApplicationContext) -> None:
        """Shows help for all available commands."""
        fields: list[tuple[str, str]] = []

        for command in self.bot.commands:
            try:
                can_run = await command.can_run(ctx)
            except (CheckFailure, CommandCheckFailure):
                can_run = False
            if not can_run:
                continue
            if isinstance(command, SlashCommand):
                fields.append((mention_command(command), command.description))
            if isinstance(command, SlashCommandGroup):
                value = (
                    command.description
                    + "\n\n"
                    + "\n".join(
                        f"{mention_command(subcommand)}: {subcommand.description}"
                        for subcommand in command.subcommands
                    )
                )
                fields.append((f"{mention_command(command)} group", value))
        new_embed = lambda: discord.Embed(title="help command")
        embeds: list[discord.Embed] = [new_embed()]
        for name, value in fields:
            if len(embeds[-1].fields) >= 5:
                embeds.append(new_embed())
            embeds[-1].add_field(name=name, value=value, inline=False)
        paginator = Paginator([Page(embeds=[embed]) for embed in embeds])
        await paginator.respond(ctx.interaction)


def setup(bot: Bot) -> None:
    """Register the HelpCog cog."""
    bot.add_cog(HelpCog(bot))
