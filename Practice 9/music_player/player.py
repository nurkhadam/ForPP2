from __future__ import annotations

from pathlib import Path
import pygame


class MusicPlayer:
    """Simple playlist-based music player using pygame.mixer.music."""

    def __init__(self, music_folder: Path):
        self.music_folder = Path(music_folder)
        self.tracks = self._load_tracks()
        self.current_index = 0
        self.is_playing = False
        self.audio_ready = self._init_mixer()
        self.track_lengths = self._read_track_lengths()

        self.music_end_event = pygame.USEREVENT + 1
        if self.audio_ready:
            pygame.mixer.music.set_endevent(self.music_end_event)

    def _init_mixer(self) -> bool:
        """Initialize the audio mixer. Return False if audio is unavailable."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return True
        except pygame.error:
            return False

    def _load_tracks(self) -> list[Path]:
        """Collect playable files from the music folder."""
        supported = {".wav", ".mp3", ".ogg"}
        tracks = sorted(
            path for path in self.music_folder.glob("*")
            if path.is_file() and path.suffix.lower() in supported
        )
        return tracks

    def _read_track_lengths(self) -> dict[str, float]:
        """Read track lengths with pygame.mixer.Sound when possible."""
        lengths: dict[str, float] = {}
        if not self.audio_ready:
            return lengths

        for track in self.tracks:
            try:
                lengths[track.name] = pygame.mixer.Sound(str(track)).get_length()
            except pygame.error:
                lengths[track.name] = 0.0
        return lengths

    def has_tracks(self) -> bool:
        return len(self.tracks) > 0

    def get_current_track(self) -> Path | None:
        if not self.has_tracks():
            return None
        return self.tracks[self.current_index]

    def play(self) -> None:
        """Play current track from the beginning."""
        if not self.audio_ready or not self.has_tracks():
            return
        current_track = self.get_current_track()
        if current_track is None:
            return
        pygame.mixer.music.load(str(current_track))
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self) -> None:
        if self.audio_ready:
            pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self, autoplay: bool = True) -> None:
        if not self.has_tracks():
            return
        self.current_index = (self.current_index + 1) % len(self.tracks)
        if autoplay:
            self.play()

    def previous_track(self, autoplay: bool = True) -> None:
        if not self.has_tracks():
            return
        self.current_index = (self.current_index - 1) % len(self.tracks)
        if autoplay:
            self.play()

    def handle_event(self, event: pygame.event.Event) -> None:
        """React to the end of a track and move to the next track automatically."""
        if self.audio_ready and event.type == self.music_end_event:
            self.next_track(autoplay=True)

    def get_position_seconds(self) -> float:
        """Current playback position in seconds."""
        if not self.audio_ready or not self.is_playing:
            return 0.0

        milliseconds = pygame.mixer.music.get_pos()
        if milliseconds < 0:
            return 0.0
        return milliseconds / 1000.0

    def get_track_length(self) -> float:
        current_track = self.get_current_track()
        if current_track is None:
            return 0.0
        return self.track_lengths.get(current_track.name, 0.0)

    def get_status_lines(self) -> list[str]:
        if not self.has_tracks():
            return ["No tracks found in music/sample_tracks"]

        track = self.get_current_track()
        status = "Playing" if self.is_playing else "Stopped"
        length = self.get_track_length()
        position = self.get_position_seconds()

        return [
            f"Status: {status}",
            f"Track: {track.name if track else 'None'}",
            f"Track {self.current_index + 1} of {len(self.tracks)}",
            f"Position: {position:05.1f}s / {length:05.1f}s",
            "Controls: P=Play  S=Stop  N=Next  B=Back  Q=Quit",
        ]