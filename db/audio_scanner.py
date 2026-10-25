import os
import asyncio
from pathlib import Path
from mutagen import File
from db.db_connection import TrackRepository

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".m4a", ".aac", ".ogg", ".wav"}

class AudioScanner:

    def __init__(self, repo: TrackRepository):
        self.repo = repo

    def _clean_string(self, value: str | None) -> str:
        return value.strip() if value else ""

    def _parse_filename(self, filepath: Path) -> tuple[str,str]:
        stem = filepath.stem

        if " - " in stem:
            parts = stem.split(" - ", 1)
            return self._clean_string(parts[1]), self._clean_string(parts[0])

        return self._clean_string(stem), ""

    def _extract_track_meta(self, filepath: Path) -> tuple[str, str] | None:

        try:
            audio = File(filepath, easy = True)

        except Exception:
            return self._parse_filename(filepath)

        if not audio:
            return self._parse_filename(filepath)

        title = audio.get("title", [None])[0]
        artist = audio.get("artist", [None])[0]

        if not title:
            fallback_title, fallback_artist = self._parse_filename(filepath)

            title = fallback_title
            artist = fallback_artist if not artist else artist

        return self._clean_string(str(title)), self._clean_string(str(artist))
    
    def _scan_disk(self, folder_path: str) -> list[tuple[str, str]]:
        root_path = Path(folder_path)

        if not root_path.exists() or not root_path.is_dir():
            raise ValueError(f"Директория не найдена: {folder_path}")
        
        tracks = []

        for root, _, files in os.walk(root_path):

            for file in files:
                path = Path(root) / file

                if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    meta = self._extract_track_meta(path)

                    if meta:
                        tracks.append(meta)

        return tracks

    async def scan_and_save(self, folder_path: str) -> int:
        
        tracks = await asyncio.to_thread(self._scan_disk, folder_path)

        if tracks:
            await self.repo.add(tracks)

        return len(tracks)