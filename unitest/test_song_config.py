import unittest
from pathlib import Path
import settings as cfg
from Logic import WrongJsonFormatError, CSVNotFoundError, MidiNotFoundError,\
    BPMNotFoundError
from Logic.song_config import SongConfig
from unitest.helpers import cases
#
#
def get_song_cfg():
    piano_mids = sorted([p for p in Path(cfg.PIANO_MIDI_PATH).iterdir()
                         if str(p).endswith('.mid')], key=lambda x: x.name)
    strings_mids = sorted([p for p in Path(cfg.STRINGS_MIDI_PATH).iterdir()
                           if str(p).endswith('.mid')], key=lambda x: x.name)
    bass_mids = sorted([p for p in Path(cfg.BASS_MIDI_PATH).iterdir()
                        if str(p).endswith('.mid')], key=lambda x: x.name)
    drums_mids = sorted([p for p in Path(cfg.DRUMS_MIDI_PATH).iterdir()
                         if str(p).endswith('.mid')], key=lambda x: x.name)

    conf = {'Name': 'easy on me',
            'Artist': '',
            'OutputPath': './WAVs/test_max_plus_one/',
            'Tracks': [{'track_name': 'Drums',
                        'midi_path': drums_mids[0]},
                       {'track_name': 'Piano',
                        'midi_path': str(piano_mids[0])},
                       {'track_name': 'Strings',
                        'midi_path': str(strings_mids[0])},
                       {'track_name': 'Bass',
                        'midi_path': str(bass_mids[0])},
                       ]}
    return SongConfig(conf)
#

class TestSuite(unittest.TestCase):

    def setUp(self):
        self.song_config = get_song_cfg()

    def tearDown(self) -> None:
        del self.song_config

    def test_init(self):

        cfg.PIANO_MIDI_PATH = '/Users/av/Development/karajan/Resources/MIDI/test_data/Piano'
        cfg.STRINGS_MIDI_PATH = '/Users/av/Development/karajan/Resources/MIDI/test_data/Strings'
        cfg.BASS_MIDI_PATH = '/Users/av/Development/karajan/Resources/MIDI/test_data/Drums'
        cfg.DRUMS_MIDI_PATH = '/Users/av/Development/karajan/Resources/MIDI/test_data/Bass'
        cfg.CSV_PATH = '/Users/av/Development/karajan/Resources/MIDI/test_data/song_bpm.csv'

        piano_mids = sorted([p for p in Path(cfg.PIANO_MIDI_PATH).iterdir()
                             if str(p).endswith('.mid')], key=lambda x: x.name)
        strings_mids = sorted([p for p in Path(cfg.STRINGS_MIDI_PATH).iterdir()
                               if str(p).endswith('.mid')], key=lambda x: x.name)
        bass_mids = sorted([p for p in Path(cfg.BASS_MIDI_PATH).iterdir()
                            if str(p).endswith('.mid')], key=lambda x: x.name)
        drums_mids = sorted([p for p in Path(cfg.DRUMS_MIDI_PATH).iterdir()
                             if str(p).endswith('.mid')], key=lambda x: x.name)

        for piano_midi, strings_midi, drums_midi, bass_midi in zip(piano_mids,
                                                                   strings_mids,
                                                                   drums_mids,
                                                                   bass_mids):
            config = {'Name': 'Test',
                      'Artist': '',
                      'OutputPath': './WAVs/test_max_plus_one/',
                      'Tracks': [{'track_name': 'Drums',
                                  'midi_path': drums_midi},
                                 {'track_name': 'Piano',
                                  'midi_path': str(piano_midi)},
                                 {'track_name': 'Strings',
                                  'midi_path': str(strings_midi)},
                                 {'track_name': 'Bass',
                                  'midi_path': str(bass_midi)},
                                 ]}
            song_config = SongConfig(config)

    @cases([['name', 'smth'], {'h', 'p'}])

    def test_init_bad(self, arguments):
        with self.assertRaises(WrongJsonFormatError):
            SongConfig(arguments)

    @cases(['/bad/path'])
    def test_load_csv_bad_path(self, arguments):
        with self.assertRaises(CSVNotFoundError):
            self.song_config.load_csv(arguments[0])

    @cases(['song_which_not_in_the_csv'])
    def test_load_csv_bad_song(self, arguments):
        self.song_config.Name = arguments
        self.song_config.load_csv(cfg.CSV_PATH)
        self.assertFalse(hasattr(self.song_config, 'BPM'))

    @cases([cfg.CSV_PATH])
    def test_load_csv_ok(self, arguments):
        self.song_config.load_csv(arguments)
        self.assertTrue(self.song_config.BPM)
        self.assertTrue(self.song_config.BPM == 71)

    def test_duplicate_midi_tmp_ok(self):
        self.song_config.duplicate_midi_tmp()
        for track in self.song_config.Tracks:
            self.assertTrue(Path(track['tmp_midi_path']).exists())

    @cases(['/bad/path/to/file.mid'])
    def test_duplicate_midi_tmp_bad(self, arguments):
        self.song_config.duplicate_midi_tmp()
        for track in self.song_config.Tracks:
            track['midi_path'] = arguments
        with self.assertRaises(MidiNotFoundError):
            self.song_config.duplicate_midi_tmp()

    def test_delete_tempo_msgs_ok(self):
        self.song_config.duplicate_midi_tmp()
        self.assertTrue(self.song_config.delete_tempo_msgs())
        self.assertFalse(self.song_config.delete_tempo_msgs())

    def test_delete_tempo_msgs_bad(self):
        with self.assertRaises(KeyError):
            self.song_config.delete_tempo_msgs()

    def test_get_bpm_from_msgs_ok(self):
        self.song_config.duplicate_midi_tmp()
        self.assertEqual(self.song_config.get_bpm_from_msgs(), 71)
        self.song_config.delete_tempo_msgs()
        self.assertEqual(self.song_config.get_bpm_from_msgs(), 120)

    def test_get_bpm_from_msgs_bad(self):
        with self.assertRaises(KeyError):
            self.song_config.get_bpm_from_msgs()

    def test_calculate_length_ok(self):
        self.song_config.BPM = 71
        self.song_config.duplicate_midi_tmp()
        self.assertNotEqual(self.song_config.calculate_length(), 224)
        self.song_config.delete_tempo_msgs()
        self.assertEqual(self.song_config.calculate_length(), 224)

    def test_calculate_length_bad1(self):
        self.song_config.BPM = None
        self.song_config.duplicate_midi_tmp()
        self.song_config.delete_tempo_msgs()
        with self.assertRaises(BPMNotFoundError):
            self.song_config.calculate_length()

    def test_calculate_length_bad2(self):
        self.assertFalse(hasattr(self, 'BPM'))
        self.song_config.duplicate_midi_tmp()
        self.song_config.delete_tempo_msgs()
        with self.assertRaises(BPMNotFoundError):
            self.song_config.calculate_length()