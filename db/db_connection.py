import aiosqlite
from typing import Literal, TypedDict

db_path = "tracks.db"
StatusType = Literal["pending", "found", "not_found", "imported"]

class TrackDict(TypedDict):
    id: int
    yandex_id: str | None
    status: StatusType
    track_name: str
    track_performer: str | None

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

    async def get(self, status: StatusType | None) -> list[TrackDict]:

        query = "SELECT * FROM user_tracks"
        params = ()

        if status is not None:
            query += " WHERE status = ?"
            params = (status,)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(query, params) as cur:
                rows = await cur.fetchall()
                return [dict(row) for row in rows]

    async def get_by_id(self, track_id: int) -> TrackDict | None:
        async with aiosqlite.connect(self.db_path) as db:

            db.row_factory = aiosqlite.Row

            async with db.execute(
                "SELECT * FROM user_tracks WHERE id = ?",
                (track_id,)
            ) as cur:
                row = await cur.fetchone()

                return dict(row) if row else None

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

    async def set_remote_id(self, id, yan_id):

        async with aiosqlite.connect(self.db_path) as db:

            db.execute("""
                UPDATE user_tracks
                SET yandex_id = ?, status = 'found'
                WHERE id = ?
            """,
            (yan_id, id)
            )
            

