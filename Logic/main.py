# import sys
import pretty_errors

from ConfigParser import ConfigParser
from RenderEngine import RenderEngine

from logger import logger_main


def main():
    """
    Process the config files.
    Creates the engine for the style.
    Creates the song with this engine.
    """
    parser = ConfigParser()  # will create __call__ later
    style_data, song_data = parser.build_song_data()
    render_engine = RenderEngine(44100, 128)
    render_engine.create_tracks(style_data)
    logger_main.info('Tracks have been created')
    render_engine.construct_graph()
    logger_main.info('Graph has been constructed')
    render_engine.process_song(song_data)


if __name__ == '__main__':
    # sys.exit(main())
    main()
    if False:
        pretty_errors
