import os

from Logic import ConfigParser, SongConfig, RenderEngine, logger_main
from pathlib import Path
import settings as cfg
from Exceptions import MidiConsistencyError

import datetime as dt

import multiprocessing
# from functools import partial

import re


def get_chunks(files, n=multiprocessing.cpu_count()):
    return [files[i::n] for i in range(n)]


def prepare_song_configs(configs):
    song_datas = []
    csv_path = cfg.CSV_PATH
    for config in configs:
        song_data = SongConfig(config)
        song_data.load_csv(csv_path)
        song_data.prepare()
        song_datas.append(song_data)
    return song_datas


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


def get_configs(midi_sets):

    def get_config(piano_midi, strings_midi, bass_midi, drums_midi):
        piano_name = piano_midi.stem.replace(' - Piano', '')
        bass_name = bass_midi.stem.replace(' - Bass', '')
        strings_name = strings_midi.stem.replace(' - Strings', '')
        drums_name = re.sub(' - Drums_\d', '', drums_midi.stem) 
        # Currently there is a problem with naming of version's keys (they are different
        # event the shift is equal
        # if not bool(piano_name == bass_name == strings_name):
        #     logger_main.debug(f'ERROR: {piano_name}, {bass_name}, {strings_name}')
        #     raise MidiConsistencyError('Wrong midi file')
        # if drums_name not in piano_name:
        #     logger_main.debug(f'ERROR: {piano_name}, {drums_name}')
        #     raise MidiConsistencyError('Wrong drums midi file')
        now = dt.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        output_path = f'./WAVs/rendering_{now}/'
        config = {'Name': piano_name,
                  'Artist': '',
                  'OutputPath': output_path,
                  'Tracks': [{'track_name': 'Drums',
                              'midi_path': str(drums_midi)},
                             {'track_name': 'Piano',
                              'midi_path': str(piano_midi)},
                             {'track_name': 'Strings',
                              'midi_path': str(strings_midi)},
                             {'track_name': 'Bass',
                              'midi_path': str(bass_midi)},
                             ]}
        return config

    configs = []
    for piano_mid, strings_mid, bass_mid, drums_mid in midi_sets:
        try:
            config = get_config(piano_mid, strings_mid, bass_mid, drums_mid)
            configs.append(config)
        except MidiConsistencyError:
            logger_main.error(f'{piano_mid.stem.replace(" - Piano", "")} has'
                              'different tracks, SKIPPED')
    return configs


def process_songs(render_engine, song_configs):

    logger_main.info(f'{len(song_configs)} is in the {os.getpid()}')
    for config in song_configs:
        logger_main.info(f'Song {config.Name} is in {os.getpid()}')
        render_engine.process_song(config)
        logger_main.info(f'Song {config.Name} has processed in {os.getpid()}')
        render_engine.save_audio(config.rendered_output_path)
    return True


def get_list_midi(path: Path):
    return sorted([p for p in path.iterdir()
                  if str(p).endswith('.mid')], key=lambda x: x.name)


def main():
    """
    Process the config files.
    Creates the engine for the style.
    Creates the song with this engine.
    """
    parser = ConfigParser()  # will create __call__ later
    style_data = parser.build_style_data(cfg.STYLE)  # style from config
    logger_main.info(f'Style {cfg.STYLE} is used.')
    render_engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
    render_engine.create_tracks(style_data)
    logger_main.info('Tracks have been created')
    render_engine.construct_graph()
    logger_main.info('Graph has been constructed')

    song_configs = get_configs(get_midi_paths_zip())
    song_configs = prepare_song_configs(song_configs, cfg)

    rendering_start = dt.datetime.now()
    process_songs(render_engine, song_configs)
    # multiprocess_song_datas(render_engine, song_datas)
    rendering = dt.datetime.now() - rendering_start
    logger_main.error('Finished Rendering, time [minutes]: '
                      f'{rendering.seconds // 60 + 1}.')


def create_and_process(song_configs):
    style = cfg.STYLE
    logger_main.info(f'Style {cfg.STYLE} is used.')
    logger_main.info(f'{len(song_configs)} is in the {os.getpid()}')

    parser = ConfigParser()  # will create __call__ later
    style_data = parser.build_style_data(style)  # style from config
    render_engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
    render_engine.create_tracks(style_data)
    render_engine.construct_graph()

    rendering_start = dt.datetime.now()

    # multiprocess_song_datas(render_engine, song_datas)

    for config in song_configs:
        logger_main.info(f'Song {config.Name} is in the {os.getpid()}')
        render_engine.process_song(config)
        logger_main.info(f'Song {config.Name} has processed in {os.getpid()}')
        render_engine.save_audio(config.rendered_output_path)

    rendering = dt.datetime.now() - rendering_start
    logger_main.error('Finished Rendering, time [minutes]: '
                      f'{rendering.seconds // 60 + 1}.')


def main_pool():
    song_configs = prepare_song_configs(get_configs(get_midi_paths_zip()))
    batches = get_chunks(song_configs)
    print(len(song_configs))

    with multiprocessing.Pool() as pool:
        pool.map(create_and_process, batches)

def main_test_as_pool():
    song_configs = prepare_song_configs(get_configs(get_midi_paths_zip()))
    create_and_process(song_configs)


if __name__ == '__main__':
    # sys.exit(main())
    # main_test_as_pool()
    main_pool()

