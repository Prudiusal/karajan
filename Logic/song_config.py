import csv

# import re
import shutil
from pathlib import Path
from uuid import uuid4

# TODO: import from Logic
from Exceptions import (
    BPMNotFoundError,
    CSVNotFoundError,
    MidiNotFoundError,
    WrongJsonFormatError,
)
from logger import logger_conf
from mido import MidiFile, tempo2bpm
from mutagen.mp3 import MP3

# from colors import red


# from itertools import groupby

# import settings as cfg


class SongConfig:
    """
    Class for the Song Configuration (just for one being used).
    """

    def __init__(self, d):
        self.Tracks = None
        self.Artist = None
        self.Name = None
        self.BPM = None
        self.OutputPath = None
        self.song_length = None
        self.rendered_output_path = None
        if not isinstance(d, dict):
            raise WrongJsonFormatError
        self.__dict__ = d

    def load_csv(self, csv_path):
        if not Path(csv_path).is_file():
            raise CSVNotFoundError(
                f"File {csv_path} doesn't exist " f"{self.Name}"
            )
        with open(csv_path, "r") as f:
            file = csv.reader(f)
            for artist, song, bpm in file:
                song = " ".join(song.split(" ")).lower()
                if song in self.Name.lower():
                    logger_conf.info(f"BPM is set to {bpm}")
                    self.BPM = int(bpm)
                    return

        if not self.check_if_playback():
            logger_conf.error(f"BPM NOT FOUND IN CSV for {self.Name}")
        return

    def check_if_playback(self):
        for track in self.Tracks:
            if track.get("mp3_path"):
                return True
        return False

    # def check_artist_excel(self):
    #     # if 'Song' in self.Artist.lower():
    #     if bool(re.match('Song\d', self.Artist)):
    #         logger_conf.error(f'Bad name of the artist {self.Artist}, '
    #                           f'{self.Name}')

    def prepare_api(self):
        self.delete_tempo_msgs()
        # Length should be calculated only for the pure midi files
        self.song_length = self.calculate_length()
        base_path = Path(self.OutputPath)
        versions_dir_path = base_path / self.Name
        versions_dir_path.mkdir(exist_ok=True, parents=True)
        song_full_path = versions_dir_path / f"{self.Name}.wav"
        self.rendered_output_path = song_full_path.absolute()

    def prepare(self):
        # self.check_artist_excel()
        self.duplicate_midi_tmp()
        # only used for pure midi configs without BPM specified
        if not (hasattr(self, "BPM") and self.check_if_playback):
            self.BPM = self.get_bpm_from_msgs()
        self.delete_tempo_msgs()
        # Length should be calculated only for the pure midi files
        self.song_length = self.calculate_length()

        base_path = Path(self.OutputPath)
        base_path.mkdir(exist_ok=True, parents=True)
        if self.check_if_playback():
            song_dir_path = base_path
            if self.Artist:
                song_full_path = (
                    song_dir_path / f"{self.Artist} -" f" {self.Name}.wav"
                )
            else:
                song_full_path = song_dir_path / f"{self.Name}.wav"
        else:
            song_dir_path = base_path / self.Name
            song_full_path = song_dir_path / f"{self.Name}.wav"
        song_dir_path.mkdir(exist_ok=True, parents=True)
        self.rendered_output_path = song_full_path.absolute()
        return True

    def calculate_length(self):
        if self.check_if_playback():
            for track in self.Tracks:
                mp3 = track.get("mp3_path")
                if mp3:
                    audio = MP3(mp3)
                    length = audio.info.length
                    logger_conf.info(f"Length {length} in {Path(mp3).name}")
                    return length

        if not hasattr(self, "BPM") or not self.BPM:
            logger_conf.fatal(
                f"{self.Name} - {self.Artist}: "
                "BPM NOT FOUND IN CONFIG, check init config "
                '(dict). Make sure you have "get_bpm_from_msgs" '
                "method of song_config. If the Playback is used,"
                ' looks as "calculate_length" not found an mp3'
            )
            raise BPMNotFoundError
        logger_conf.warning(f"Bmp {self.BPM} is used")
        times = []
        for track in self.Tracks:
            # path = track.get('tmp_midi_path', track.get('midi_path'))
            path = track["tmp_midi_path"]
            try:
                mid = MidiFile(str(path))
            except Exception as e:
                logger_conf.error(e)
                continue
            times.append(mid.length)
        length = max(times) + 1
        k = 120 / self.BPM  # default tempo corresponds to bpm=120
        return int(k * length)

    def delete_tempo_msgs(self):
        flag = False
        for song_track in self.Tracks:
            midi_file = song_track.get("tmp_midi_path")
            if not midi_file:
                continue
            # TODO: look for the mido exceptions
            mid = MidiFile(midi_file)
            for i, track in enumerate(mid.tracks):
                track_filtered = [
                    msg for msg in track if msg.type != "set_tempo"
                ]
                if len(track_filtered) != len(track):
                    flag = True
                mid.tracks[i] = track_filtered
            mid.save(midi_file)
        return flag

    def get_bpm_from_msgs(self):
        for song_track in self.Tracks:
            midi_file = song_track.get("tmp_midi_path")
            if not midi_file:
                continue
            mid = MidiFile(midi_file)
            bpms = []
            for i, track in enumerate(mid.tracks):
                bpms.extend(
                    [
                        int(tempo2bpm(msg.tempo))
                        for msg in track
                        if msg.type == "set_tempo"
                    ]
                )
                # ms = [msg.type for msg in track
                #       if msg.type not in ['note_on', 'note_off']]
                # # print(red(str(bpms)))
                # # print(red(str(ms)))
            if not len(bpms):
                logger_conf.error("Tempo messages not found!")
                return 120
            elif len(bpms) == 1 or len(set(bpms)) == 1:
                logger_conf.info(f"Tempo {bpms[0]} found")
                return bpms[0]
            else:
                logger_conf.error(f"FOUND {len(set(bpms))} : {set(bpms)}")
                logger_conf.error(f"{bpms[0]} is used")
                return bpms[0]

    def duplicate_midi_tmp(self):
        """
        Creates copy of the song in ./tmp folder
        This allows to change the midi files while
        the processing, without changing the original file
        """
        self.tmp_path = Path(".") / "tmp" / "midi"
        # print(self.tmp_path.absolute())
        self.tmp_path.mkdir(parents=True, exist_ok=True)
        # self.tmp_path = Path(cfg.TMP_MIDI_PATH)
        for track in self.Tracks:
            if track.get("midi_path"):
                new_name = str(uuid4()) + ".mid"
                tmp_midi_path = self.tmp_path / new_name
                if not Path(track["midi_path"]).exists():
                    raise MidiNotFoundError
                shutil.copy(track["midi_path"], tmp_midi_path.absolute())
                logger_conf.debug(
                    f'{track["midi_path"]} copied into '
                    f"{str(self.tmp_path)} as "
                    f"{new_name}"
                )
                track["tmp_midi_path"] = tmp_midi_path.absolute()
