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
    style_data = parser.build_style_data('automidi')
    render_engine = RenderEngine(44100, 128)
    render_engine.create_tracks(style_data)
    logger_main.info('Tracks have been created')
    render_engine.construct_graph()
    logger_main.info('Graph has been constructed')

    songs = ['7-Rings',
             ]
    #         'blow_out_my_candle',
    #         'easy_lover',
    #         'maybe_youre_the_problem',
    #         'break_my_soul',
    #         'sigala',
    #         'about_damn_time',
    #         'what_you_were_made_for',
    #         'what_i_want',
    #         'where_did_you_go',
    #         'living_without_you',
    #         'stay_the_night',
    #         'sacrifice'
    #         ]

    for song in songs:
        logger_main.info(f'{song} is in process')
        song_data = parser.build_midi_data(song)
        logger_main.info(f'Midi data build for {song} ')
        render_engine.process_song(song_data)
        logger_main.info(f'Song {song} is processed')
        render_engine.save_audio()


if __name__ == '__main__':
    # sys.exit(main())
    main()
    if False:
        pretty_errors
