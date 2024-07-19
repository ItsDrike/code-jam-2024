import aiohttp

CAT_URL: str = "https://api.thecatapi.com/v1/images/search"


async def getcatimageurl() -> str:
    """Get an image of a random cat."""
    async with aiohttp.ClientSession() as client, client.get(CAT_URL) as response:
        response.raise_for_status()
        data = await response.json()
        return data[0]["url"]
