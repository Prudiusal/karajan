from Logic import ConfigParser, SongConfig, RenderEngine, logger_main
from pathlib import Path
import settings as cfg
import pretty_errors
# from ConfigParser import ConfigParser, SongConfig
# from RenderEngine import RenderEngine


# from logger import


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
    # drum_midi = './Resources/MIDI/piano_drums/drums/sample1.mid'
    piano_mids_path = Path('Resources/MIDI/test_data/Piano')
    strings_mids_path = Path('Resources/MIDI/test_data/Strings')
    drums_mids_path = Path('Resources/MIDI/test_data/Drums')
    bass_mids_path = Path('Resources/MIDI/test_data/Bass')
    csv_path = 'Resources/MIDI/test_data/song_bpm.csv'

    # uncomment, to move to the .env values
    # piano_mids_path = Path(cfg.PIANO_MIDI_PATH)
    # strings_mids_path = Path(cfg.STRINGS_MIDI_PATH)
    # drums_mids_path = Path(cfg.DRUMS_MIDI_PATH)
    # bass_mids_path = Path(cfg.BASS_MIDI_PATH)
    # csv_path = cfg.CSV_PATH

    piano_midi_files = sorted([p for p in piano_mids_path.iterdir()
                               if str(p).endswith('.mid')], key=lambda x: x.name)
    strings_midi_files = sorted([p for p in strings_mids_path.iterdir()
                                 if str(p).endswith('.mid')], key=lambda x: x.name)
    bass_midi_files = sorted([p for p in bass_mids_path.iterdir()
                              if str(p).endswith('.mid')], key=lambda x: x.name)
    drums_midi_files = sorted([p for p in drums_mids_path.iterdir()
                               if str(p).endswith('.mid')], key=lambda x: x.name)

    # we are zipping the lists of file in order to iterate over multiple files
    for piano_midi, strings_midi, drums_midi, bass_midi in zip(piano_midi_files,
                                                               strings_midi_files,
                                                               drums_midi_files,
                                                               bass_midi_files):


        # outfile will have the name like a piano and drum midi files
        logger_main.warning(f'{str(piano_midi)}, {str(strings_midi)}')
        # name = '_'.join([piano_midi.stem, Path(drum_midi).stem])
        # name = piano_midi.stem.lower().replace(' Piano')
        name = piano_midi.stem.lower()
        if not 'amy' in name:
            continue

        # creation of the config (json-style) for the track
        config = {'Name': name,
                  'Artist': '',
                  'OutputPath': './WAVs/test_del/',
                  'Tracks': [{'track_name': 'Drums',
                              'midi_path': drums_midi},
                             {'track_name': 'Piano',
                              'midi_path': str(piano_midi)},
                             {'track_name': 'Strings',
                              'midi_path': str(strings_midi)},
                             {'track_name': 'Bass',
                              'midi_path': str(bass_midi)},
                             ]}
        logger_main.info(f'{piano_midi.stem} is in process')
        song_data = SongConfig(config)
        song_data.load_csv(csv_path)
        song_data.prepare()
        render_engine.process_song(song_data)
        logger_main.info(f'Song {piano_midi.stem} has processed')
        render_engine.save_audio(song_data.rendered_output_path)


if __name__ == '__main__':
    import sys
    print(sys.path)
    # sys.exit(main())
    main()
    if False:
        pretty_errors
