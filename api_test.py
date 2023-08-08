import requests
from pathlib import Path
import settings as cfg
from time import sleep


URL = 'http://localhost:8000/upload'


def get_midi_paths_zip():
    piano_mids_path = Path(cfg.PIANO_MIDI_PATH)
    strings_mids_path = Path(cfg.STRINGS_MIDI_PATH)
    drums_mids_path = Path(cfg.DRUMS_MIDI_PATH)
    bass_mids_path = Path(cfg.BASS_MIDI_PATH)

    piano_midi_files = sorted([p for p in piano_mids_path.iterdir()
                               if str(p).endswith('.mid')],
                              key=lambda x: x.name)
    strings_midi_files = sorted([p for p in strings_mids_path.iterdir()
                                 if str(p).endswith('.mid')],
                                key=lambda x: x.name)
    bass_midi_files = sorted([p for p in bass_mids_path.iterdir()
                              if str(p).endswith('.mid')],
                             key=lambda x: x.name)
    drums_midi_files = sorted([p for p in drums_mids_path.iterdir()
                               if str(p).endswith('.mid')],
                              key=lambda x: x.name)

    return zip(piano_midi_files,
               strings_midi_files,
               bass_midi_files,
               drums_midi_files)


if __name__ == '__main__':
    midis = get_midi_paths_zip()
    for piano, strings, bass, drums in midis:

        name = piano.stem.replace(' - Piano', '')
        files_paths = {'piano_midi': piano,
                       'strings_midi': strings,
                       'bass_midi': bass,
                       'drums_midi': drums}
        files = {k: open(v, 'rb') for k, v in files_paths.items()}
        data = {'bpm': 128,
                'name': name}
        response = requests.post(URL, data=data, files=files)
        print(response)
        sleep(2)
