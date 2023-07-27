import os
import datetime as dt
import multiprocessing

import settings as cfg
from Logic import ConfigParser, JsonConfigCreator, RenderEngine, logger_main
from Logic import SongConfig


def get_chunks(files, n=multiprocessing.cpu_count()):
    return [files[i::n] for i in range(n)]


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

    configs_creator = JsonConfigCreator()
    midis = configs_creator.get_midi_paths_zip()
    song_configs = configs_creator.get_configs_midi(midis)
    song_configs = configs_creator.prepare_song_configs(song_configs)

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
        if not isinstance(config, SongConfig):
            logger_main.error(f'Wrong config type: {config}')
            continue
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

    configs_creator = JsonConfigCreator()
    midis = configs_creator.get_midi_paths_zip()
    song_configs = configs_creator.get_configs_midi(midis)
    song_configs = configs_creator.prepare_song_configs(song_configs)

    batches = get_chunks(song_configs)

    with multiprocessing.Pool() as pool:
        pool.map(create_and_process, batches)


def main_pool_wav():

    configs_creator = JsonConfigCreator()
    song_dirs = configs_creator.get_stem_paths()
    song_configs = configs_creator.get_configs_stem(song_dirs)
    song_configs = configs_creator.prepare_song_configs(song_configs)

    batches = get_chunks(song_configs)

    with multiprocessing.Pool() as pool:
        pool.map(create_and_process, batches)


def main_test_as_pool():
    configs_creator = JsonConfigCreator()
    midis = configs_creator.get_midi_paths_zip()
    song_configs = configs_creator.get_configs_midi(midis)
    song_configs = configs_creator.prepare_song_configs(song_configs)
    create_and_process(song_configs)


def main_test_as_pool_wav():
    configs_creator = JsonConfigCreator()
    song_dirs = configs_creator.get_stem_paths()
    song_configs_dict = configs_creator.get_configs_stem(song_dirs)
    song_configs = configs_creator.prepare_song_configs(song_configs_dict)
    create_and_process(song_configs)


if __name__ == '__main__':
    # sys.exit(main())
    # main_test_as_pool()
    # main_pool()
    # main_test_as_pool_wav()
    main_pool_wav()
