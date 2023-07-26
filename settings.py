from os import environ
import platform

from dotenv import load_dotenv

load_dotenv()

# style, which determines the set of plugins
STYLE = environ.get('STYLE')
APPLY_SELECTION = 1

# RenderEngine parameters
SAMPLE_RATE = int(environ.get('SAMPLE_RATE', 44100))
BUFFER_SIZE = int(environ.get('BUFFER_SIZE', 128))

# Locations of the midi file, set in the .env
PIANO_MIDI_PATH = environ.get('PIANO_MIDI_PATH')
BASS_MIDI_PATH = environ.get('BASS_MIDI_PATH')
STRINGS_MIDI_PATH = environ.get('STRINGS_MIDI_PATH')
DRUMS_MIDI_PATH = environ.get('DRUMS_MIDI_PATH')

# path parameters, used in a project
CSV_PATH = environ.get('CSV_PATH')
TMP_MIDI_PATH = environ.get('TMP_MIDI_PATH')
LOG_PATH = environ.get('LOG_PATH')

# stems to connect together
if platform.system() == 'Windows':
    STEMS_ROOT_PATH = environ.get('STEMS_ROOT_PATH')
    STYLE_CONFIG_PATH = environ.get('STYLE_CONFIG_PATH')
    OUTPUT_PATH = environ.get('OUTPUT_PATH')
    EXCEL_SHEET_PATH = environ.get('EXCEL_SHEET_PATH')
    STEMS_CSV_PATH = environ.get('STEMS_CSV_PATH')
else:
    STEMS_ROOT_PATH = environ.get('STEMS_ROOT_PATH_MAC')
    STYLE_CONFIG_PATH = environ.get('STYLE_CONFIG_PATH_MAC')
    OUTPUT_PATH = environ.get('OUTPUT_PATH_MAC')
    EXCEL_SHEET_PATH = environ.get('EXCEL_SHEET_PATH_MAC')
    STEMS_CSV_PATH = environ.get('STEMS_CSV_PATH_MAC')
