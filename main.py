import os

from Logic import ConfigParser, SongConfig, RenderEngine, logger_main
from pathlib import Path
import settings as cfg

import datetime

import multiprocessing
from functools import partial


def get_chunks(files, n=multiprocessing.cpu_count()):
    return [files[i::n] for i in range(n)]


def multiengines_process_batch():
    engines = []
    for i in range(multiprocessing.cpu_count):
        engines.append()


def multiprocess_song_datas(render_engine, song_datas):
    # DEPRECATED
    num_cores = multiprocessing.cpu_count()
    chunks = get_chunks(song_datas, num_cores)
    with multiprocessing.get_context('spawn').Pool(processes=num_cores) as pool:
        # L = pool.starmap(func, chunks)
        # M = pool.starmap(func, zip(chunks, repeat(render_engine)))
        # pool.map(process_song_datas, (chunks, render_engine))
        pool.map(partial(process_songs, render_engine=render_engine),
                 chunks)


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
    configs = []
    for piano_midi, strings_midi, bass_midi, drums_midi in midi_sets:
        name = piano_midi.stem.lower()
        config = {'Name': name,
                  'Artist': '',
                  'OutputPath': './WAVs/test_mp/',
                  'Tracks': [{'track_name': 'Drums',
                              'midi_path': str(drums_midi)},
                             {'track_name': 'Piano',
                              'midi_path': str(piano_midi)},
                             {'track_name': 'Strings',
                              'midi_path': str(strings_midi)},
                             {'track_name': 'Bass',
                              'midi_path': str(bass_midi)},
                             ]}

        configs.append(config)
    return configs


def process_songs(render_engine, song_configs):

    logger_main.info(f'{len(song_configs)} is in the {os.getpid()}')
    for config in song_configs:
        logger_main.info(f'Song {config.Name} is in the processing in {os.getpid()}')
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

    rendering_start = datetime.datetime.now()
    process_songs(render_engine, song_configs)
    # multiprocess_song_datas(render_engine, song_datas)
    rendering = datetime.datetime.now() - rendering_start
    logger_main.error('Finished Rendering, time [minutes]: '
                      f'{rendering.seconds // 60 + 1}.')





def create_song_config_batches():
    song_configs = prepare_song_configs(get_configs(get_midi_paths_zip()))

def main_parallel():
    engines = create_engines()
    song_configs = prepare_song_configs(get_configs(get_midi_paths_zip()))
    batches = get_chunks(song_configs)
    input()

    assert len(batches) == len(engines)

    processes = []
    for engine, batch in zip(engines, batches):
        p = multiprocessing.Process(target=process_songs, args=(engine, batch, ))
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

def create_engines():
    style = cfg.STYLE
    logger_main.info(f'Style {cfg.STYLE} is used.')

    engines = []

    parser = ConfigParser()  # will create __call__ later
    style_data = parser.build_style_data(style)  # style from config

    for _ in range(multiprocessing.cpu_count()):
        render_engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
        render_engine.create_tracks(style_data)
        render_engine.construct_graph()
        engines.append(render_engine)
    return engines

def create_and_process(song_configs):
    style = cfg.STYLE
    logger_main.info(f'Style {cfg.STYLE} is used.')
    logger_main.info(f'{len(song_configs)} is in the {os.getpid()}')

    parser = ConfigParser()  # will create __call__ later
    style_data = parser.build_style_data(style)  # style from config
    render_engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
    render_engine.create_tracks(style_data)
    render_engine.construct_graph()

    rendering_start = datetime.datetime.now()

    # multiprocess_song_datas(render_engine, song_datas)

    for config in song_configs:
        logger_main.info(f'Song {config.Name} is in the processing in {os.getpid()}')
        render_engine.process_song(config)
        logger_main.info(f'Song {config.Name} has processed in {os.getpid()}')
        render_engine.save_audio(config.rendered_output_path)

    rendering = datetime.datetime.now() - rendering_start
    logger_main.error('Finished Rendering, time [minutes]: '
                      f'{rendering.seconds // 60 + 1}.')


def main_pool():
    song_configs = prepare_song_configs(get_configs(get_midi_paths_zip()))
    batches = get_chunks(song_configs)

    with multiprocessing.Pool() as pool:
        pool.map(create_and_process, batches)




if __name__ == '__main__':
    # sys.exit(main())
    main_pool()

