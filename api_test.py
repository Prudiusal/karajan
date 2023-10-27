from pathlib import Path
from time import sleep

import requests

import settings as cfg

# URL = "http://localhost:8000/upload"
host_api = cfg.HOST
port_api = cfg.PORT
URL = f"http://{host_api}:{port_api}/upload"


def get_midi_paths_zip():
    piano_mids_path = Path(cfg.TEST_PIANO_MIDI_PATH)
    strings_mids_path = Path(cfg.TEST_STRINGS_MIDI_PATH)
    drums_mids_path = Path(cfg.TEST_DRUMS_MIDI_PATH)
    bass_mids_path = Path(cfg.TEST_BASS_MIDI_PATH)

    piano_midi_files = sorted(
        [p for p in piano_mids_path.iterdir() if str(p).endswith(".mid")],
        key=lambda x: x.name,
    )
    strings_midi_files = sorted(
        [p for p in strings_mids_path.iterdir() if str(p).endswith(".mid")],
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
        piano_midi_files, strings_midi_files, bass_midi_files, drums_midi_files
    )


if __name__ == "__main__":
    midis = get_midi_paths_zip()
    for piano, strings, bass, drums in midis:
        name = piano.stem.replace(" - Piano", "")
        files_paths = {
            "piano_midi": piano,
            "strings_midi": strings,
            "bass_midi": bass,
            "drums_midi": drums,
        }
        files = {k: open(v, "rb") for k, v in files_paths.items()}
        data = {"bpm": 128, "name": name}
        response = requests.post(URL, data=data, files=files)
        print(response)
        sleep(10)
