from typing import Literal, overload

from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapters.media import ensure_media
from src.db_tables.user_list import UserList, UserListItem, UserListItemKind


@overload
async def list_put_item(
    session: AsyncSession,
    user_list: UserList,
    tvdb_id: int,
    kind: Literal[UserListItemKind.MOVIE, UserListItemKind.SERIES],
) -> UserListItem: ...


@overload
async def list_put_item(
    session: AsyncSession,
    user_list: UserList,
    tvdb_id: int,
    kind: Literal[UserListItemKind.EPISODE],
    series_id: int,
) -> UserListItem: ...


async def list_put_item(
    session: AsyncSession, user_list: UserList, tvdb_id: int, kind: UserListItemKind, series_id: int | None = None
) -> UserListItem:
    """Add an item to a user list.

    :raises ValueError: If the item is already present in the list.
    """
    async with session:
        if series_id:
            await ensure_media(session, tvdb_id, kind, series_id=series_id)
        else:
            await ensure_media(session, tvdb_id, kind)
        if await session.get(UserListItem, (user_list.id, tvdb_id, kind)) is not None:
            raise ValueError(f"Item {tvdb_id} is already in list {user_list.id}.")

        item = UserListItem(list_id=user_list.id, tvdb_id=tvdb_id, kind=kind)
        session.add(item)
        await session.commit()
        return item


async def list_get_item(
    session: AsyncSession, user_list: UserList, tvdb_id: int, kind: UserListItemKind
) -> UserListItem | None:
    """Get an item from a user list."""
    async with session:
        return await session.get(UserListItem, (user_list.id, tvdb_id, kind))


async def list_remove_item(session: AsyncSession, user_list: UserList, item: UserListItem) -> UserList:
    """Remove an item from a user list."""
    async with session:
        item = await session.merge(item)
        user_list = await session.merge(user_list)
        await session.delete(item)
        await session.commit()
        await session.refresh(user_list, ["items"])
        return user_list


async def list_remove_item_safe(
    session: AsyncSession, user_list: UserList, tvdb_id: int, kind: UserListItemKind
) -> UserList:
    """Removes an item from a user list if it exists."""
    async with session:
        if item := await list_get_item(session, user_list, tvdb_id, kind):
            return await list_remove_item(session, user_list, item)
        return user_list


@overload
async def list_put_item_safe(
    session: AsyncSession,
    user_list: UserList,
    tvdb_id: int,
    kind: Literal[UserListItemKind.MOVIE, UserListItemKind.SERIES],
) -> UserListItem: ...


@overload
async def list_put_item_safe(
    session: AsyncSession,
    user_list: UserList,
    tvdb_id: int,
    kind: Literal[UserListItemKind.EPISODE],
    series_id: int,
) -> UserListItem: ...


async def list_put_item_safe(
    session: AsyncSession, user_list: UserList, tvdb_id: int, kind: UserListItemKind, series_id: int | None = None
) -> UserListItem:
    """Add an item to a user list, or return the existing item if it is already present."""
    async with session:
        if series_id:
            await ensure_media(session, tvdb_id, kind, series_id=series_id)
        else:
            await ensure_media(session, tvdb_id, kind)
        item = await list_get_item(session, user_list, tvdb_id, kind)
        if item:
            return item

        item = UserListItem(list_id=user_list.id, tvdb_id=tvdb_id, kind=kind)
        session.add(item)
        await session.commit()
        return item


async def refresh_list_items(session: AsyncSession, user_list: UserList) -> UserList:
    """Refresh the items in a user list."""
    async with session:
        user_list = await session.merge(user_list)
        await session.refresh(user_list, ["items"])
        return user_list


async def get_list_item(
    session: AsyncSession,
    user_list: UserList,
    tvdb_id: int,
    kind: UserListItemKind,
) -> UserListItem | None:
    """Get a user list."""
    async with session:
        return await session.get(UserListItem, (user_list.id, tvdb_id, kind))