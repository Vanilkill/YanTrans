import aiosqlite
from typing import Literal

db_path = "tracks.db"
StatusType = Literal["pending", "found", "not_found", "imported"]

class TrackRepository:
    def __init__(self, db_path: str = db_path):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("PRAGMA journal_mode = WAL;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_tracks(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    yandex_id TEXT DEFAULT NULL,
                    status TEXT DEFAULT 'pending',
                    track_name TEXT NOT NULL,
                    track_performer TEXT DEFAULT NULL
                )
            """
            )

            await db.commit()

        print(">>> База данных инициализирована")

    async def add(self, tracks: list[tuple[str,str]]):
        async with aiosqlite.connect(self.db_path) as db:

            db.executemany(
                "INSERT INTO user_tracks (track_name, track_performer) VALUES (?, ?);",
                tracks
            )

            await db.commit()

    async def get(self, status: StatusType | None) -> list[tuple]:

        query = "SELECT track_name, track_performer FROM user_tracks"
        params = ()

        if status is not None:
            query += " WHERE status = ?"
            params = (status,)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cur:
                return await cur.fetchall()

    async def set_status(self, id: int, status: StatusType):

        async with aiosqlite.connect(self.db_path) as db:

            db.execute("""
                UPDATE user_tracks
                SET status = ?
                WHERE id = ?
            """,
            (status, id)
            )

            await db.commit()

    async def update_find_status(self, id: int, status: bool):

        _status = "found" if status else "not_found"

        await self.set_status(id, _status)

    async def update_import_status(self, id, status: bool):

        _status = "imported" if status else "found"
        
        await self.set_status(id, _status)
            

