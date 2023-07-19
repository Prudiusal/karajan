import os

from pathlib import Path
import settings as cfg

import datetime as dt

# from functools import partial
from Logic import ConfigParser, SongConfig, RenderEngine, logger_main
from Logic import Selector
from Exceptions import MidiConsistencyError, CSVNotFoundError

import multiprocessing
from itertools import zip_longest
# import re


def get_chunks(files, n=multiprocessing.cpu_count()):
    return [files[i::n] for i in range(n)]


def prepare_song_configs(configs: dict):
    song_datas = []
    csv_path = cfg.CSV_PATH
    for config in configs:
        song_data = SongConfig(config)
        try:
            song_data.load_csv(csv_path)
        except CSVNotFoundError as e:
            if not song_data.check_if_playback():
                logger_main.error(e)
            logger_main.warning(e)
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


def get_stem_paths():
    stem_dir = Path(cfg.STEMS_ROOT_PATH)
    artist_dirs = [d for d in stem_dir.iterdir() if d.is_dir()]
    song_dirs = []
    for song_dir in artist_dirs:
        song_dirs.extend([d for d in song_dir.iterdir() if d.is_dir()])
        # song_dirs.extend(= [list(d.iterdir()) for d in artist_dirs if
        # d.is_dir()]
    if not song_dirs:
        raise ValueError('Directory with stems is empty')
    return song_dirs


def get_configs_stem(paths):
    selector = Selector()

    def get_config_mp3(files_mp3, files_steps, name, artist):
        now = dt.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        output_path = f'./WAVs/stem_rendering_{now}/'
        name = name.replace(artist, '').rstrip()
        config = {'Name': name,
                  'Artist': artist,
                  'OutputPath': output_path,
                  'Tracks': []}
        if len(files_mp3) != len(files_steps):
            logger_main.debug('Different number of steps and mp3 for the track'
                              f'{name}: {len(files_mp3)=} and '
                              f'{len(files_steps)=}')
            files_steps = [False]
            input()
        for i, files in enumerate(zip_longest(files_mp3, files_steps)):
            mp3, steps = files
            # probably there is no need in "type" field
            stem_name = mp3.stem.replace(name, '').rstrip()
            stem_name = stem_name.replace(artist, '').rstrip()
            stem_name = stem_name.replace('--', '').rstrip()
            config['Tracks'].append({'track_name': f'instrument_{i}',
                                     'mp3_path': mp3,
                                     'steps_path': steps,
                                     'stem_name': stem_name
                                     })
        return config

    configs = []
    for song_dir in paths:
        files_mp3 = [f.absolute() for f in song_dir.iterdir()
                     if f.suffix == '.mp3']
        files_steps = [f.absolute() for f in song_dir.iterdir()
                       if f.suffix == '.json' and f.stem.endswith('steps')]
        song_name = song_dir.name
        artist_name = str(song_dir.absolute()).split(os.sep)[-2]
        config = get_config_mp3(files_mp3, files_steps, song_name, artist_name)

        if cfg.APPLY_SELECTION:
            config = selector(config)
        configs.append(config)

    return configs


def get_configs_midi(midi_sets):

    def get_config_midi(piano_midi, strings_midi, bass_midi, drums_midi):
        piano_name = piano_midi.stem.replace(' - Piano', '')
        # bass_name = bass_midi.stem.replace(' - Bass', '')
        # strings_name = strings_midi.stem.replace(' - Strings', '')
        # drums_name = re.sub(' - Drums_\d', '', drums_midi.stem)
        # Currently there is a problem with naming of version's keys (they are
        # different event the shift is equal
        # if not bool(piano_name == bass_name == strings_name):
        #     logger_main.debug(f'ERROR: {piano_name}, {bass_name},
        # {strings_name}')
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
            config = get_config_midi(piano_mid, strings_mid, bass_mid,
                                     drums_mid)
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

    song_configs = get_configs_midi(get_midi_paths_zip())
    song_configs = prepare_song_configs(song_configs, cfg)

    rendering_start = dt.datetime.now()
    process_songs(render_engine, song_configs)
    # multiprocess_song_datas(render_engine, song_datas)
    rendering = dt.datetime.now() - rendering_start
    logger_main.info('Finished Rendering, time [minutes]: '
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
        # Change process song -> wav or midi
        # config.setup_engine(render_engine)
        render_engine.process_song(config)
        logger_main.info(f'Song {config.Name} has processed in {os.getpid()}')
        render_engine.save_audio(config.rendered_output_path)

    rendering = dt.datetime.now() - rendering_start
    logger_main.info('Finished Rendering, time [minutes]: '
                     f'{rendering.seconds // 60 + 1}.')


def main_pool():
    #
    # if cfg.WAv_MODE:
    #     one type of configs
    # else:
    #     another type of configs

    song_configs = prepare_song_configs(get_configs_midi(get_midi_paths_zip()))

    batches = get_chunks(song_configs)
    print(len(song_configs))

    with multiprocessing.Pool() as pool:
        pool.map(create_and_process, batches)


def main_pool_wav():
    configs = prepare_song_configs(get_configs_stem(get_stem_paths()))
    batches = get_chunks(configs)

    with multiprocessing.Pool() as pool:
        pool.map(create_and_process, batches)


def main_test_as_pool():
    song_configs = prepare_song_configs(get_configs_midi(get_midi_paths_zip()))
    create_and_process(song_configs)


def main_test_as_pool_wav():
    song_configs = prepare_song_configs(get_configs_stem(get_stem_paths()))
    create_and_process(song_configs)


if __name__ == '__main__':
    # sys.exit(main())
    # main_test_as_pool()
    # main_pool()
    # main_test_as_pool_wav()
    main_pool_wav()