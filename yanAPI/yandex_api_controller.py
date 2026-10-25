from yandex_music import ClientAsync
from db.db_connection import TrackRepository

class YandexController:
    def __init__(self, repo: TrackRepository, token):
        self.token = token
        self.client: ClientAsync | None = None

        self.repo = repo

    async def init(self):
        self.client = await ClientAsync(self.token).init()

    async def find_tracks(self):
        tracks = await self.repo.get("pending")
        