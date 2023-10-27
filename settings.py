import platform
from os import environ

from dotenv import load_dotenv

load_dotenv()

# style, which determines the set of plugins
STYLE = environ.get("STYLE")
APPLY_SELECTION = 1

# RenderEngine parameters
SAMPLE_RATE = int(environ.get("SAMPLE_RATE", 44100))
BUFFER_SIZE = int(environ.get("BUFFER_SIZE", 128))
HOST = environ.get("HOST", "0:0:0:0")
PORT = int(environ.get("PORT", "8000"))

LOG_PATH = environ.get("LOG_PATH")

# stems to connect together
if platform.system() == "Windows":
    # Locations of the midi file, set in the .env
    PIANO_MIDI_PATH = environ.get("PIANO_MIDI_PATH")
    BASS_MIDI_PATH = environ.get("BASS_MIDI_PATH")
    STRINGS_MIDI_PATH = environ.get("STRINGS_MIDI_PATH")
    DRUMS_MIDI_PATH = environ.get("DRUMS_MIDI_PATH")
    # Locations of the midi files, used in tests
    TEST_PIANO_MIDI_PATH = environ.get("TEST_PIANO_MIDI_PATH")
    TEST_BASS_MIDI_PATH = environ.get("TEST_BASS_MIDI_PATH")
    TEST_STRINGS_MIDI_PATH = environ.get("TEST_STRINGS_MIDI_PATH")
    TEST_DRUMS_MIDI_PATH = environ.get("TEST_DRUMS_MIDI_PATH")
    # path parameters, used in a project
    CSV_PATH = environ.get("CSV_PATH")
    TEST_CSV_PATH = environ.get("TEST_CSV_PATH")
    TMP_MIDI_PATH = environ.get("TMP_MIDI_PATH")

    STEMS_ROOT_PATH = environ.get("STEMS_ROOT_PATH")
    STYLE_CONFIG_PATH = environ.get("STYLE_CONFIG_PATH")
    OUTPUT_PATH = environ.get("OUTPUT_PATH")
    EXCEL_SHEET_PATH = environ.get("EXCEL_SHEET_PATH")
    STEMS_CSV_PATH = environ.get("STEMS_CSV_PATH")
else:
    # Locations of the midi file, set in the .env
    PIANO_MIDI_PATH = environ.get("PIANO_MIDI_PATH_MAC")
    BASS_MIDI_PATH = environ.get("BASS_MIDI_PATH_MAC")
    STRINGS_MIDI_PATH = environ.get("STRINGS_MIDI_PATH_MAC")
    DRUMS_MIDI_PATH = environ.get("DRUMS_MIDI_PATH_MAC")
    # path parameters, used in a project
    CSV_PATH = environ.get("CSV_PATH_MAC")
    TMP_MIDI_PATH = environ.get("TMP_MIDI_PATH_MAC")

    STEMS_ROOT_PATH = environ.get("STEMS_ROOT_PATH_MAC")
    STYLE_CONFIG_PATH = environ.get("STYLE_CONFIG_PATH_MAC")
    OUTPUT_PATH = environ.get("OUTPUT_PATH_MAC")
    EXCEL_SHEET_PATH = environ.get("EXCEL_SHEET_PATH_MAC")
    STEMS_CSV_PATH = environ.get("STEMS_CSV_PATH_MAC")
