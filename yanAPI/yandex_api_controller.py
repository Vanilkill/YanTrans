from yandex_music import ClientAsync
from db.db_connection import TrackRepository
from yanAPI.authorize_window import Authorize

class YandexController:
    def __init__(self, repo: TrackRepository, token):
        self.token = token
        self.client: ClientAsync | None = None

        self.repo = repo

    async def init(self):
        self.client = await ClientAsync(self.token).init()

    async def find_tracks(self):
        tracks = await self.repo.get("pending")

        for track in tracks:
            query = f"{track["track_performer"]} {track["track_name"]}"

            result = await self.client.search(text=query, type_="track")

            if result.tracks and result.tracks.results:
                best = result.tracks.results[0]
                await self.repo.set_remote_id(track[0], str(best.id))

                print(f"Трек найден! id = {best.id}")
                continue

            await self.repo.update_find_status(False)
            print("Трек не найден!")

    async def add_to_like_tracks(self):
        tracks = await self.repo.get("found")

        for track in tracks:
            result = await self.client.users_likes_tracks_add(track_ids = track["yandex_id"])
            await self.repo.update_import_status(track[0], result)

            print("Трек добавлен!") if result else print("<<<Трек не добавлен...>>>")
