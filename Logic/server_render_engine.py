import os
from time import sleep
import multiprocessing

from RenderEngine import RenderEngine
from ConfigParser import ConfigParser
from song_config import SongConfig
from logger import logger_server


class ServerRenderEngine(RenderEngine):

    def __init__(self, queue, style_data, sr=44100, buffer=128):

        super().__init__(sample_rate=sr, buffer_size=buffer)
        self.queue = queue
        self.create_tracks(style_data)
        self.construct_graph()
        self.serve_forever()

    def serve_forever(self):
        print(f'RenderEngine started {os.getpid()}')
        while True:
            if not self.queue.empty():
                json_song_config = self.queue.get()
                song_config = SongConfig(json_song_config)
                logger_server.info(f'{song_config.Name} in {os.getpid()}')
                try:
                    song_config.prepare_api()
                except Exception as e:
                    logger_server.error(e)
                    continue
                logger_server.info(f'Song {song_config.Name} - config created')
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

                logger_server.info(f'Song {song_config.Name} has processed in '
                                   f'{os.getpid()}')

            else:
                sleep(1)


class ServerRunner:

    def __init__(self, queue, n_proc: int = None, style: str = None):
        self.n_proc = n_proc if n_proc else multiprocessing.cpu_count()
        self.style = style if style else 'PianoDrums'
        self.parser = ConfigParser()
        self.queue = queue

    def run_engines(self):
        style_data = self.parser.build_style_data(style=self.style)
        for _ in range(self.n_proc):
            process = multiprocessing.Process(target=ServerRenderEngine,
                                              args=(self.queue, style_data))
            process.start()
