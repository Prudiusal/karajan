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

    # The song_data object is created on a base of dictionary
    # Here the dicts are created with the midi files of the folders.
    drum_midi = './Resources/MIDI/piano_drums/drums/sample1.mid'
    piano_mids_path = Path('./Resources/MIDI/piano_drums/piano')
    strings_mids_path = Path('./Resources/MIDI/piano_drums/strings')
    piano_midi_files = sorted([p for p in piano_mids_path.iterdir()
                               if not str(p.stem).startswith('.')])
    strings_midi_files = sorted([p for p in strings_mids_path.iterdir()
                                 if not str(p.stem).startswith('.')])

    # we are zipping the lists of file in order to iterate over multiple files
    for piano_midi, strings_midi in zip(piano_midi_files, strings_midi_files):
        # outfile will have the name like a piano and drum midi files
        logger_main.warning(f'{str(piano_midi)}, {str(strings_midi)}')
        name = '_'.join([piano_midi.stem, Path(drum_midi).stem])
        # creation of the config (json-style) for the track
        config = {'Name': name,
                  'Artist': 'NoBPM',
                  'OutputPath': './WAVs/test/',
                  # 'BPM': 75,
                  'Tracks': [{'track_name': 'Drums',
                              'midi_path': drum_midi},
                             {'track_name': 'Piano',
                              'midi_path': str(piano_midi)},
                             {'track_name': 'Strings',
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
