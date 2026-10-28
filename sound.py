"""音效、歌曲播放、TTS 语音。"""
import os
import random
import threading
import queue
import config


class SoundManager:
    def __init__(self, app):
        self.app = app
        self.mixer_ok = False
        self.tts_ok = False
        self.lyric_error = None
        self._tts_queue = queue.Queue()
        self._init_mixer()
        self._init_tts()

    def _init_mixer(self):
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.pygame = pygame
            self.mixer_ok = True
        except Exception:
            self.mixer_ok = False

    def _init_tts(self):
        try:
            import win32com.client
            self._win32 = win32com.client
            self.tts_ok = True
            threading.Thread(target=self._tts_worker, daemon=True).start()
        except Exception:
            self.tts_ok = False

    def _tts_worker(self):
        import pythoncom
        pythoncom.CoInitialize()
        speaker = None
        while True:
            text = self._tts_queue.get()
            if text is None:
                break
            try:
                if speaker is None:
                    speaker = self._win32.Dispatch("SAPI.SpVoice")
                speaker.Speak(text, 1)
            except Exception as e:
                print(f"[tts失败] {type(e).__name__}: {e}")
                speaker = None
            finally:
                self._tts_queue.task_done()

    def speak(self, text):
        if not self.tts_ok:
            return
        self._tts_queue.put(text)

    def load_songs(self):
        songs = []
        exts = (".mp3", ".wav", ".ogg", ".amr", ".m4a", ".flac")
        if os.path.isdir(config.SONG_DIR):
            for f in os.listdir(config.SONG_DIR):
                if f.lower().endswith(exts) or "." not in f:
                    songs.append(os.path.join(config.SONG_DIR, f))
        return songs

    def try_play(self, track):
        if not self.mixer_ok:
            return False
        try:
            self.pygame.mixer.music.load(track)
            self.pygame.mixer.music.play()
            return True
        except Exception as e:
            print(f"[播放失败] {track}: {e}")
            return False

    def play_song(self, app):
        songs = app.songs
        if not (self.mixer_ok and songs):
            return False, "songs/ 里还没有歌"
        track = random.choice(songs)
        if self.try_play(track):
            return True, os.path.basename(track)
        wav = self._convert_to_wav(track)
        if wav and self.try_play(wav):
            return True, os.path.basename(wav)
        return False, os.path.basename(track)

    def _convert_to_wav(self, track):
        try:
            from pydub import AudioSegment
            wav = os.path.splitext(track)[0] + ".wav"
            if os.path.exists(wav):
                return wav
            AudioSegment.from_file(track).export(wav, format="wav")
            return wav
        except Exception as e:
            print(f"[转码失败] {e}")
            return None

    def play(self, name):
        """播放内置小音效（sounds/<name>.wav）"""
        if not self.mixer_ok:
            return
        path = os.path.join(config.SOUND_DIR, f"{name}.wav")
        if os.path.exists(path):
            try:
                self.pygame.mixer.Sound(path).play()
            except Exception:
                pass

    def start_bgm(self, app):
        if not self.mixer_ok:
            return
        songs = app.songs
        if not songs:
            return
        track = random.choice(songs)
        try:
            self.pygame.mixer.music.load(track)
            self.pygame.mixer.music.play(-1)
        except Exception:
            pass

    def stop_bgm(self):
        if self.mixer_ok:
            try:
                self.pygame.mixer.music.stop()
            except Exception:
                pass
