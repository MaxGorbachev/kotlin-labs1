import aiosqlite
import asyncio

db_name = 'userdata.db'


# USERS
async def get_user_data(tg_id):
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    data = await db.execute(f'SELECT * FROM users WHERE tg_id == "{tg_id}"')
    return await data.fetchone()


async def create_user(tg_id):
    db = await aiosqlite.connect(db_name)
    await db.execute(f'INSERT INTO users (tg_id) values ("{tg_id}")')
    await db.commit()
    return await get_user_data(tg_id)


async def change_user_status(tg_id, new_status: str) -> None:
    db = await aiosqlite.connect(db_name)
    await db.execute(f'update users set status = "{new_status}" WHERE tg_id == "{tg_id}"')
    await db.commit()


async def get_users():
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    data = await db.execute(f'SELECT * FROM users')
    return await data.fetchall()


async def add_message(tg_id: int, message_id):
    try:
        db = await aiosqlite.connect(db_name)
        old_messages = await get_messages(tg_id)
        if not old_messages:
            old_messages = []
        old_messages.append(str(message_id))
        data = " ".join(old_messages)
        await db.execute(f'update users set messages_to_delete = "{data}" WHERE tg_id == "{tg_id}"')
        await db.commit()
        return True
    except Exception:
        return False


async def get_messages(tg_id):
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    messages = await db.execute(f'SELECT messages_to_delete FROM users WHERE tg_id == "{tg_id}"')
    messages = (await messages.fetchone())['messages_to_delete']
    if messages:
        return messages.split()
    return False


async def clear_messages(tg_id):
    db = await aiosqlite.connect(db_name)
    await db.execute(f'update users set messages_to_delete = NULL WHERE tg_id == "{tg_id}"')
    await db.commit()


# CHANNELS
async def get_channels():
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    channels = await db.execute(f'SELECT * FROM channels')
    return await channels.fetchall()


async def get_channel(channel_url):
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    channel = await db.execute(f'SELECT * FROM channels where url = "{channel_url}"')
    return await channel.fetchone()


async def delete_channel(channel_url):
    channel = await get_channel(channel_url)
    if channel:
        db = await aiosqlite.connect(db_name)
        await db.execute(f'DELETE from channels where url = "{channel_url}" ')
        await db.commit()
        return True
    return False


async def add_channel(title, link):
    db = await aiosqlite.connect(db_name)
    await db.execute(f'INSERT INTO channels (url, title) values ("{link}", "{title}")')
    await db.commit()


# FILMS

async def get_films():
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    films = await db.execute(f'SELECT * FROM films')
    return await films.fetchall()


async def get_film(id):
    db = await aiosqlite.connect(db_name)
    db.row_factory = aiosqlite.Row
    film = await db.execute(f'SELECT * FROM films where id = "{id}"')
    return await film.fetchone()


async def add_film(title, link, description):
    db = await aiosqlite.connect(db_name)
    await db.execute(f'INSERT INTO films (image_url, title, description) values ("{link}", "{title}", "{description}")')
    await db.commit()


async def delete_film(id):
    film = await get_film(id)
    if film:
        db = await aiosqlite.connect(db_name)
        await db.execute(f'DELETE from films where id = "{id}" ')
        await db.commit()
        return True
    return False
