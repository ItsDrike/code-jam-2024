from collections.abc import Sequence
from typing import Literal

import discord
from discord import ApplicationContext, Cog, option, slash_command

from src.bot import Bot
from src.db_adapters import refresh_list_items, user_get_list
from src.db_tables.user_list import UserListItem, UserListItemKind
from src.tvdb import Episode, FetchMeta, Movie, Series, TvdbClient
from src.tvdb.errors import InvalidIdError
from src.utils.log import get_logger
from src.utils.ratelimit import rate_limited

from .ui import InfoView

log = get_logger(__name__)

MOVIE_EMOJI = "🎬"
SERIES_EMOJI = "📺"


async def fetch_items(tvdb_client: TvdbClient, items: list[UserListItem]) -> tuple[list[Movie], list[Episode]]:
    """Fetch the items from the tvdb API."""
    movies = []
    episodes = []

    for item in items:
        if item.kind == UserListItemKind.MOVIE:
            movies.append(await Movie.fetch(item.tvdb_id, client=tvdb_client, extended=False))
        elif item.kind == UserListItemKind.EPISODE:
            episodes.append(await Episode.fetch(item.tvdb_id, client=tvdb_client, extended=True))

    return movies, episodes


def compare_lists(
    items: Sequence[Movie | Episode], other_items: Sequence[Movie | Episode]
) -> Sequence[Movie | Episode]:
    """Compare two lists of items and return the common items."""
    items_set = {item.id for item in items}
    set(items_set)
    other_items_set = {item.id for item in other_items}
    set(other_items_set)

    common_ids = items_set & other_items_set

    items_dict = {item.id: item for item in items}

    return [items_dict[item_id] for item_id in common_ids]


class InfoCog(Cog):
    """Cog to show information about a movie or a series."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.tvdb_client = TvdbClient(self.bot.http_session, self.bot.cache)

    @slash_command()
    @option("query", input_type=str, description="The query to search for.")
    @option(
        "type",
        input_type=str,
        parameter_name="entity_type",
        description="The type of entity to search for.",
        choices=["movie", "series"],
        required=False,
    )
    @option("by_id", input_type=bool, description="Search by tvdb ID.", required=False)
    @rate_limited(key=lambda self, ctx: f"{ctx.user}", limit=2, period=8, update_when_exceeded=True, prefix_key=True)
    async def search(
        self,
        ctx: ApplicationContext,
        *,
        query: str,
        entity_type: Literal["movie", "series"] | None = None,
        by_id: bool = False,
    ) -> None:
        """Search for a movie or series."""
        await ctx.defer()

        if by_id:
            if query.startswith("movie-"):
                entity_type = "movie"
                query = query[6:]
            elif query.startswith("series-"):
                entity_type = "series"
                query = query[7:]
            try:
                match entity_type:
                    case "movie":
                        response = [
                            await Movie.fetch(query, self.tvdb_client, extended=True, meta=FetchMeta.TRANSLATIONS)
                        ]
                    case "series":
                        response = [
                            await Series.fetch(query, self.tvdb_client, extended=True, meta=FetchMeta.TRANSLATIONS)
                        ]
                    case None:
                        await ctx.respond(
                            "You must specify a type (movie or series) when searching by ID.", ephemeral=True
                        )
                        return
            except InvalidIdError:
                await ctx.respond(
                    'Invalid ID. Id must be an integer, or "movie-" / "series-" followed by an integer.',
                    ephemeral=True,
                )
                return
        else:
            response = await self.tvdb_client.search(query, limit=5, entity_type=entity_type)
            if not response:
                await ctx.respond("No results found.")
                return

        view = InfoView(self.bot, ctx.user.id, response)
        await view.send(ctx.interaction)

    @slash_command()
    @option("other", input_type=discord.Member, description="The other user to compare with.")
    async def compare(self, ctx: ApplicationContext, *, other: discord.Member) -> None:
        """Compare your lists with another user."""
        await ctx.defer()

        user_list = await user_get_list(self.bot.db_session, ctx.user.id, "watched")
        if not user_list:
            await ctx.respond("You have no watched items.", ephemeral=True)
            return
        await refresh_list_items(self.bot.db_session, user_list)
        if not user_list.items:
            await ctx.respond("You have no watched items.", ephemeral=True)
        other_user_list = await user_get_list(self.bot.db_session, other.id, "watched")
        if not other_user_list:
            await ctx.respond(f"{other.display_name} has no watched items.", ephemeral=True)
            return
        await refresh_list_items(self.bot.db_session, other_user_list)
        if not other_user_list.items:
            await ctx.respond(f"{other.display_name} has no watched items.", ephemeral=True)
            return

        movies, episodes = await fetch_items(self.tvdb_client, user_list.items)

        other_movies, other_episodes = await fetch_items(self.tvdb_client, other_user_list.items)

        common_movies = compare_lists(movies, other_movies)
        common_episodes = compare_lists(episodes, other_episodes)

        embed = discord.Embed(title="Common Items", color=discord.Color.blurple())
        if common_movies:
            movie_names = "\n".join(f"{MOVIE_EMOJI} {movie.name}" for movie in common_movies)
            embed.add_field(name="Movies", value=movie_names)
        if common_episodes:
            episode_names = "\n".join(f"{SERIES_EMOJI} {episode.name}" for episode in common_episodes)
            embed.add_field(name="Episodes", value=episode_names)

        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    """Register the PingCog cog."""
    bot.add_cog(InfoCog(bot))
