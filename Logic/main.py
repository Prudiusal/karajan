# import sys
from pathlib import Path
import pretty_errors
from ConfigParser import ConfigParser, SongConfig
from RenderEngine import RenderEngine


from logger import logger_main


def main():
    """
    Process the config files.
    Creates the engine for the style.
    Creates the song with this engine.
    """
    parser = ConfigParser()  # will create __call__ later
    style_data = parser.build_style_data('PianoDrums')  # style from config
    render_engine = RenderEngine(44100, 128)
    render_engine.create_tracks(style_data)
    logger_main.info('Tracks have been created')
    render_engine.construct_graph()
    logger_main.info('Graph has been constructed')

    drum_midi = './Resources/MIDI/piano_drums/drums/sample1.mid'
    piano_mids_path = Path('./Resources/MIDI/piano_drums/piano')
    strings_mids_path = Path('./Resources/MIDI/piano_drums/strings')
    piano_midi_files = sorted(piano_mids_path.iterdir())
    strings_midi_files = sorted(strings_mids_path.iterdir())

    for piano_midi, strings_midi in zip(piano_midi_files, strings_midi_files):
        # outfile will have the name like a piano and drum midi files
        name = '_'.join([piano_midi.stem, Path(drum_midi).stem])
        config = {'Name': name,
                  'Artist': 'NikitaTikhomirov',
                  'OutputPath': './WAVs/test/',
                  'BPM': 75,
                  'Tracks': [{'track_name': 'Drums',  # change
                              'midi_path': drum_midi},
                             {'track_name': 'Piano',  # change
                              'midi_path': str(piano_midi)},
                             {'track_name': 'Strings',  # change
                              'midi_path': str(strings_midi)}
                             ]}
        logger_main.info(f'{piano_midi.stem} is in process')
        song_data = SongConfig(config)
        render_engine.process_song(song_data)
        logger_main.info(f'Song {piano_midi.stem} is processed')
        render_engine.save_audio()


if __name__ == '__main__':
    # sys.exit(main())
    main()
    if False:
        pretty_errors
