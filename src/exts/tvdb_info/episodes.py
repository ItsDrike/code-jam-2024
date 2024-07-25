import discord

from src.tvdb.client import Series
from src.tvdb.generated_models import EpisodeBaseRecord


class EpisodesView(discord.ui.View):
    """Episode View."""

    def __init__(self, episodes: EpisodeBaseRecord, series: Series):
        super().__init__()
