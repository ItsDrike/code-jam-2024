import aiohttp


async def get_cat_image_url() -> None:
    """Get an image of a random cat."""
    async with (
        aiohttp.ClientSession() as session,
        session.get("https://api.thecatapi.com/v1/images/search") as resp,
    ):
        if resp.status == 200:
            data = await resp.json()
            return data[0]["url"]
        else:  # noqa: RET505
            return None
