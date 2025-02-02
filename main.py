import datetime as dt
import multiprocessing
import os
from argparse import ArgumentParser

import settings as cfg
from Logic import (  # ServerRenderEngine,
    ConfigParser,
    JsonConfigCreator,
    RenderEngine,
    SongConfig,
    logger_main,
)

# from functools import reduce
# from itertools import cycle
# from typing import Dict


def get_chunks(files, n=multiprocessing.cpu_count()):
    """
    The function `get_chunks` takes a list of files and splits it into multiple
    chunks based on the number of available CPU cores.

    :param files: The "files" parameter is a list of file names or file paths
    :param n: The parameter `n` is the number of chunks to divide the files
    into. By default, it is set
    to the number of available CPU cores on the system, which is obtained using
    the `multiprocessing.cpu_count()` function
    :return: a list of chunks of files. Each chunk contains a subset of the
    files list, with each element in the chunk being separated by a step size
    of n. The value of n is set to the number of CPU cores available on the
    system by default.
    """
    return [files[i::n] for i in range(n)]


def create_and_process(song_configs):
    """
    The function `create_and_process` takes a list of song configurations,
    processes each song using a render engine, and saves the rendered output
    as audio files.

    :param song_configs: A list of SongConfig objects that contain the
    configuration for each song to be processed
    """
    style = cfg.STYLE
    logger_main.info(f"Style {cfg.STYLE} is used.")
    logger_main.info(f"{len(song_configs)} is in the {os.getpid()}")

    parser = ConfigParser()  # will create __call__ later
    style_data = parser.build_style_data(style)  # style from config
    render_engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
    render_engine.create_tracks(style_data)
    render_engine.construct_graph()

    rendering_start = dt.datetime.now()

    for config in song_configs:
        if not isinstance(config, SongConfig):
            logger_main.error(f"Wrong config type: {config}")
            continue
        logger_main.info(f"Song {config.Name} is in the {os.getpid()}")
        # Change process song -> wav or midi
        # config.setup_engine(render_engine)
        render_engine.process_song(config)
        logger_main.info(f"Song {config.Name} has processed in {os.getpid()}")
        render_engine.save_audio(config.rendered_output_path)

    rendering = dt.datetime.now() - rendering_start
    logger_main.info(
        "Finished Rendering, time [minutes]: "
        f"{rendering.seconds // 60 + 1}."
    )


def main_pool(num_workers):
    """
    The main_pool function creates and processes song configurations in
    parallel using multiprocessing.

    :param num_workers: The parameter "num_workers" represents the number of
    worker processes to use in the multiprocessing pool. It determines how many
    parallel processes will be created to execute the "create_and_process"
    function
    """
    configs_creator = JsonConfigCreator()
    midis = configs_creator.get_midi_paths_zip()
    song_configs = configs_creator.get_configs_midi(midis)
    song_configs = configs_creator.prepare_song_configs(song_configs)

    batches = get_chunks(song_configs, num_workers)

    with multiprocessing.Pool(num_workers) as pool:
        pool.map(create_and_process, batches)


def main_pool_wav(n_workers):
    """
    Used for Stems
    The `main_pool_wav` function uses multiprocessing to create and process
    batches of song configurations.

    :param n_workers: The parameter `n_workers` represents the number of worker
    processes to use in the multiprocessing pool. It determines how many
    parallel processes will be created to execute the `create_and_process`
    function
    """
    configs_creator = JsonConfigCreator()
    song_dirs = configs_creator.get_stem_paths()
    song_configs = configs_creator.get_configs_stem(song_dirs)
    song_configs = configs_creator.prepare_song_configs(song_configs)

    batches = get_chunks(song_configs, n_workers)

    with multiprocessing.Pool(n_workers) as pool:
        pool.map(create_and_process, batches)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Render midi files with multiple processes"
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of process for rendering (default: CPU count)",
    )
    args = parser.parse_args()
    num_workers = args.num_workers
    main_pool(num_workers)
    # sys.exit(main())
    # main_test_as_pool()
    # main_test_as_pool_wav()
    # main_pool_wav(num_workers)
