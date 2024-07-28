from sqlalchemy.ext.asyncio import AsyncSession


async def refresh[T](session: AsyncSession, item: T, fields: list[str]) -> T:
    """Refresh a media item with the specified fields."""
    async with session:
        item = await session.merge(item)
        await session.refresh(item, fields)
        return item
