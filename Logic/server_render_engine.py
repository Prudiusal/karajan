import multiprocessing
import os
from time import sleep

from ConfigParser import ConfigParser
from logger import logger_server
from RenderEngine import RenderEngine
from song_config import SongConfig


# The `ServerRenderEngine` class is a subclass of `RenderEngine` that serves as
# a server for processing and rendering songs based on configurations received
# from a queue.
# The `ServerRenderEngine` class is a subclass of `RenderEngine` that
# initializes with a queue, style data, sample rate, and buffer size, creates
# tracks based on the style data, constructs a graph, and serves forever.
class ServerRenderEngine(RenderEngine):
    def __init__(self, queue, style_data, sr=44100, buffer=128):
        """
        The function initializes an object with a queue, style data, sample
        rate, and buffer size, creates tracks based on the style data,
        constructs a graph, and serves forever.

        :param queue: The `queue` parameter is used to pass midi data between
        different parts of the code. It can be a `JoinableQueue` object from
        the `multiprocessing` module in Python, which allows for thread-safe
        communication between different threads or processes
        :param style_data: The `style_data` parameter is a data structure that
        contains information about the style of the audio tracks.
        It could include things like the tracks, plugins, and any other
        characteristics that define the style of the music. This data will be
        used to create the tracks and construct the audio processing graph.
        :param sr: The parameter "sr" stands for sample rate, which refers to
        the number of samples per second in an audio signal.
        It determines the quality and fidelity of the audio. In this case,
        the default value is set to 44100, which is a common sample rate used
        in audio production, defaults to 44100 (optional)
        :param buffer: The "buffer" parameter refers to the size of the audio
        buffer used for processing audio data. It determines the amount of
        audio data that is processed at a time. A larger buffer size can reduce
        the risk of audio glitches or dropouts, but it also increases the
        latency of the audio processing. The, defaults to 128 (optional)
        """
        super().__init__(sample_rate=sr, buffer_size=buffer)
        self.queue = queue
        self.create_tracks(style_data)
        self.construct_graph()
        self.serve_forever()

    def serve_forever(self):
        """
        The function `serve_forever` continuously checks for items in a queue,
        processes them, and saves the output, logging any errors encountered
        along the way.
        """
        print(f"RenderEngine started {os.getpid()}")
        while True:
            if not self.queue.empty():
                json_song_config = self.queue.get()
                song_config = SongConfig(json_song_config)
                logger_server.info(f"{song_config.Name} in {os.getpid()}")
                try:
                    song_config.prepare_api()
                except Exception as e:
                    logger_server.error(e)
                    continue
                logger_server.info(f"Song {song_config.Name} - config created")
                try:
                    self.process_song(song_config)
                except Exception as e:
                    logger_server.error(e)
                    continue
                try:
                    self.save_audio(song_config.rendered_output_path)
                except Exception as e:
                    logger_server.error(e)
                    continue

                logger_server.info(
                    f"Song {song_config.Name} has processed in "
                    f"{os.getpid()}"
                )

            else:
                sleep(1)


# The `ServerRunner` class initializes with a queue, number of processes, and
# style, and has a method to run multiple instances of the `ServerRenderEngine`
# class in separate processes.
class ServerRunner:
    def __init__(self, queue, n_proc: int = None, style: str = None):
        """
        The function initializes an object with optional parameters and assigns
        values to instance variables.

        :param queue: The `queue` parameter is a queue object that is used for
        communication between different processes. It allows for passing data
        between processes in a thread-safe manner
        :param n_proc: The `n_proc` parameter is an optional integer that
        specifies the number of processes to use for parallel processing. If
        not provided, it defaults to the number of CPUs available on the system
        :type n_proc: int
        :param style: The "style" parameter is used to specify the style of
        music. It is a string that represents the desired style, such as
        "PianoDrums". If no style is provided, the default value is
        "PianoDrums". The Style should be described in
        ./Resources/Configs/StylesConfig.json.
        :type style: str
        """
        self.n_proc = n_proc if n_proc else multiprocessing.cpu_count()
        self.style = style if style else "PianoDrums"
        self.parser = ConfigParser()
        self.queue = queue

    def run_engines(self):
        """
        The function `run_engines` starts multiple processes to run the
        `ServerRenderEngine` function with a queue and style data as arguments.
        """
        style_data = self.parser.build_style_data(style=self.style)
        for _ in range(self.n_proc):
            process = multiprocessing.Process(
                target=ServerRenderEngine, args=(self.queue, style_data)
            )
            process.start()
