import unittest
from pathlib import Path

import settings as cfg
from Logic import (
    BPMNotFoundError,
    ConfigParser,
    RenderEngine,
    SongConfig,
    TracksNotFoundError,
    WrongStyleType,
)


def get_song_cfg():
    piano_mids = sorted(
        [
            p
            for p in Path(cfg.TEST_PIANO_MIDI_PATH).iterdir()
            if str(p).endswith(".mid")
        ],
        key=lambda x: x.name,
    )
    strings_mids = sorted(
        [
            p
            for p in Path(cfg.TEST_STRINGS_MIDI_PATH).iterdir()
            if str(p).endswith(".mid")
        ],
        key=lambda x: x.name,
    )
    bass_mids = sorted(
        [
            p
            for p in Path(cfg.TEST_BASS_MIDI_PATH).iterdir()
            if str(p).endswith(".mid")
        ],
        key=lambda x: x.name,
    )
    drums_mids = sorted(
        [
            p
            for p in Path(cfg.TEST_DRUMS_MIDI_PATH).iterdir()
            if str(p).endswith(".mid")
        ],
        key=lambda x: x.name,
    )

    conf = {
        "Name": "easy on me",
        "Artist": "",
        "OutputPath": "./WAVs/test_max_plus_one/",
        "Tracks": [
            {"track_name": "Drums", "midi_path": drums_mids[0]},
            {"track_name": "Piano", "midi_path": str(piano_mids[0])},
            {"track_name": "Strings", "midi_path": str(strings_mids[0])},
            {"track_name": "Bass", "midi_path": str(bass_mids[0])},
        ],
    }
    return SongConfig(conf)


class TestSuite(unittest.TestCase):
    def setUp(self):
        parser = ConfigParser()
        self.style_data = parser.build_style_data(cfg.STYLE)
        self.song_config = get_song_cfg()

        self.engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)

    def tearDown(self) -> None:
        del self.engine
        del self.style_data
        del self.song_config

    def test_create_tracks_ok(self):
        self.engine.create_tracks(self.style_data)

    def test_create_tracks_bad(self):
        with self.assertRaises(WrongStyleType):
            self.engine.create_tracks([])

    def test_construct_graph_ok(self):
        self.engine.create_tracks(self.style_data)
        self.engine.construct_graph()

    def test_construct_graph_bad(self):
        with self.assertRaises(TracksNotFoundError):
            self.engine.construct_graph()

    def test_process_song(self):
        self.song_config.load_csv(cfg.TEST_CSV_PATH)
        self.song_config.prepare()
        self.engine.create_tracks(self.style_data)
        self.engine.construct_graph()
        self.engine.process_song(self.song_config)

    def test_process_song_bad(self):
        # self.song_config.load_csv(cfg.CSV_PATH)
        # self.song_config.prepare()
        self.engine.create_tracks(self.style_data)
        self.engine.construct_graph()
        with self.assertRaises(BPMNotFoundError):
            self.engine.process_song(self.song_config)

    def test_load_data_into_tracks_ok(self):
        self.song_config.load_csv(cfg.TEST_CSV_PATH)
        self.song_config.prepare()
        self.engine.create_tracks(self.style_data)
        self.engine.construct_graph()
        self.engine.load_data_into_tracks(self.song_config)

    def test_load_data_into_tracks_bad(self):
        self.song_config.load_csv(cfg.TEST_CSV_PATH)
        self.song_config.prepare()
        self.engine.create_tracks(self.style_data)
        # self.engine.construct_graph() # nothing will be created
        self.engine.load_data_into_tracks(self.song_config)
