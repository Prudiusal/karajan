import csv
import datetime as dt
import os
import re
from itertools import zip_longest
from pathlib import Path

from Exceptions import (
    CSVNotFoundError,
    MidiConsistencyError,
    MP3NotFoundError,
    MP3NotSuiteStepsJsonError,
    StemsCSVNotFoundError,
    StemsDeletionError,
    StemsNotDeletedError,
    StepsNotFoundError,
    UnableToDeleteStemsError,
)
from logger import logger_json
from selector import Selector
from song_config import SongConfig

import settings as cfg

# import openpyxl


class JsonConfigCreator:
    output_path = ""

    @staticmethod
    def get_stem_paths():
        stem_dir = Path(cfg.STEMS_ROOT_PATH)
        artist_dirs = [d for d in stem_dir.iterdir() if d.is_dir()]
        song_dirs = []
        for song_dir in artist_dirs:
            song_dirs.extend([d for d in song_dir.iterdir() if d.is_dir()])
            # song_dirs.extend(= [list(d.iterdir()) for d in artist_dirs if
            # d.is_dir()]
        if not song_dirs:
            raise ValueError("Directory with stems is empty")
        return song_dirs

    @staticmethod
    def get_midi_paths_zip():
        piano_mids_path = Path(cfg.PIANO_MIDI_PATH)
        strings_mids_path = Path(cfg.STRINGS_MIDI_PATH)
        drums_mids_path = Path(cfg.DRUMS_MIDI_PATH)
        bass_mids_path = Path(cfg.BASS_MIDI_PATH)

        piano_midi_files = sorted(
            [p for p in piano_mids_path.iterdir() if str(p).endswith(".mid")],
            key=lambda x: x.name,
        )
        strings_midi_files = sorted(
            [
                p
                for p in strings_mids_path.iterdir()
                if str(p).endswith(".mid")
            ],
            key=lambda x: x.name,
        )
        bass_midi_files = sorted(
            [p for p in bass_mids_path.iterdir() if str(p).endswith(".mid")],
            key=lambda x: x.name,
        )
        drums_midi_files = sorted(
            [p for p in drums_mids_path.iterdir() if str(p).endswith(".mid")],
            key=lambda x: x.name,
        )

        return zip(
            piano_midi_files,
            strings_midi_files,
            bass_midi_files,
            drums_midi_files,
        )

    def get_config_mp3(self, files_mp3, files_steps, name, artist):
        name = name.replace(artist, "").rstrip()
        config = {
            "Name": name,
            "Artist": artist,
            "OutputPath": str(self.output_path.absolute()),
            "Tracks": [],
        }
        if not files_mp3:
            raise MP3NotFoundError(f"{name} doesn't have MP3 files, skipped")
        elif not files_steps:
            raise StepsNotFoundError(
                f"{name} doesn't have STEPS json " "files, skipped"
            )

        if len(files_mp3) != len(files_steps):
            raise MP3NotSuiteStepsJsonError(
                "Different number of steps and mp3"
                f"for the track {name}: "
                f"{len(files_mp3)=} and "
                f"{len(files_steps)=}"
            )

        for i, files in enumerate(zip_longest(files_mp3, files_steps)):
            mp3, steps = files
            stem_name = mp3.stem.replace(name, "").rstrip()
            stem_name = stem_name.replace(artist, "").rstrip()
            stem_name = stem_name.replace("--", "").rstrip()
            config["Tracks"].append(
                {
                    "track_name": f"instrument_{i}",
                    "mp3_path": mp3,
                    "steps_path": steps,
                    "stem_name": stem_name,
                }
            )
        return config

    def get_configs_stem(self, paths):
        now = dt.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        self.output_path = Path(cfg.OUTPUT_PATH) / f"stem_rendering_{now}"

        selector = Selector()
        configs = []
        for song_dir in paths:
            files_mp3 = [
                f.absolute() for f in song_dir.iterdir() if f.suffix == ".mp3"
            ]
            files_steps = [
                f.absolute()
                for f in song_dir.iterdir()
                if f.suffix == ".json" and f.stem.endswith("steps")
            ]

            song_name = song_dir.name
            artist_name = str(song_dir.absolute()).split(os.sep)[-2]
            try:
                config = self.get_config_mp3(
                    files_mp3, files_steps, song_name, artist_name
                )
            except (
                MP3NotFoundError,
                StepsNotFoundError,
                MP3NotSuiteStepsJsonError,
            ) as e:
                logger_json.error(e)
                # logger_json.error(f'File {song_name} has skipped')
                continue

            if cfg.APPLY_SELECTION:
                try:
                    config = selector(config)
                except (
                    StemsDeletionError,
                    StemsNotDeletedError,
                    UnableToDeleteStemsError,
                ) as e:
                    logger_json.critical(e)
                    # logger_json.error(f'File {song_name} has skipped')
                    continue

                # if num_tracks_init == num_tracks_new:
                #    logger_json.error(f'{config.get("Name")}: The same amount'
                #                       'of tracks after selection')
                #     logger_json.error(f'File {song_name} has skipped')
                #     continue
            configs.append(config)
        self.check_artist_names(configs)
        return configs

    def check_artist_names(self, configs):
        bad_configs = []
        pattern = r"Song\d"
        for config in configs:
            if bool(re.match(pattern, config["Artist"])):
                logger_json.error(
                    f'Bad name of the artist {config["Artist"]},'
                    f' {config["Name"]}'
                )
                bad_configs.append(config)
        if bad_configs:
            self.correct_artist_names(bad_configs)
            try:
                self.correct_artist_names(bad_configs)
            except (StemsCSVNotFoundError,) as e:
                logger_json.error(e)
                return None
            return True

    def correct_artist_names(self, bad_configs):
        stems_csv_path = cfg.STEMS_CSV_PATH
        if not Path(stems_csv_path).exists():
            raise StemsCSVNotFoundError
        with open(stems_csv_path, "r", encoding="utf-8") as f:
            file = csv.reader(f)
            mapper = {}
            for raw_row in file:
                row = raw_row[0].split(";")
                id_csv = row[0]
                artist = row[1]
                mapper[id_csv] = artist

        for bad_config in bad_configs:
            id_from_folders = bad_config.get("Artist")
            artist_name = mapper.get(id_from_folders)
            # if artist_name == '':
            #     artist_name = ''
            bad_config["Artist"] = artist_name
            logger_json.info(f"{id_from_folders} is changed to {artist_name}")
        return True

    @staticmethod
    def prepare_song_configs(configs: dict):
        song_datas = []
        csv_path = cfg.CSV_PATH
        for config in configs:
            song_data = SongConfig(config)
            try:
                song_data.load_csv(csv_path)
            except CSVNotFoundError as e:
                if not song_data.check_if_playback():
                    logger_json.error(e)
                logger_json.warning(e)
            song_data.prepare()
            song_datas.append(song_data)
        return song_datas

    def get_config_midi(self, piano_midi, strings_midi, bass_midi, drums_midi):
        piano_name = piano_midi.stem.replace(" - Piano", "")
        bass_name = bass_midi.stem.replace(" - Bass", "")
        strings_name = strings_midi.stem.replace(" - Strings", "")
        drums_name = re.sub(" - Drums_\d", "", drums_midi.stem)
        # Currently there is a problem with naming of version's keys (they are
        # different event the shift is equal
        if not bool(piano_name == bass_name == strings_name):
            logger_json.debug(
                f"ERROR: {piano_name}, {bass_name}," f"{strings_name}"
            )
            raise MidiConsistencyError("Wrong midi file")
        if drums_name not in piano_name:
            logger_json.debug(f"ERROR: {piano_name}, {drums_name}")
            raise MidiConsistencyError("Wrong drums midi file")

        config = {
            "Name": piano_name,
            "Artist": "",
            "OutputPath": self.output_path,
            "Tracks": [
                {"track_name": "Drums", "midi_path": str(drums_midi)},
                {"track_name": "Piano", "midi_path": str(piano_midi)},
                {"track_name": "Strings", "midi_path": str(strings_midi)},
                {"track_name": "Bass", "midi_path": str(bass_midi)},
            ],
        }
        return config

    def get_configs_midi(self, midi_sets):
        configs = []
        now = dt.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        self.output_path = f"./WAVs/rendering_{now}/"

        for piano_mid, strings_mid, bass_mid, drums_mid in midi_sets:
            try:
                config = self.get_config_midi(
                    piano_mid, strings_mid, bass_mid, drums_mid
                )
                configs.append(config)
            except MidiConsistencyError:
                logger_json.error(
                    f'{piano_mid.stem.replace(" - Piano", "")} '
                    "has different tracks, SKIPPED"
                )
        return configs
