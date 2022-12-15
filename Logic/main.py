import sys

from ConfigParser import ConfigParser
from MidiVST import MidiVST
from RenderEngine import RenderEngine

from logger import logger_main


def main():
    # :TODO Add auto-parsing and creation of instruments class instances if
    # found by name
    parser = ConfigParser(separate=False)
    song_data = parser.build_song_data()
    song_data = ConfigParser.build_song_data()
    logger_main.debug(f'{type(song_data)=}')
    logger_main.info(repr(song_data))
    render_engine = RenderEngine(44100, 128)
    serum = MidiVST(song_data.synth_path, song_data.preset_path,
                    song_data.midi_path)

    # :TODO 1.These loads should happen inside MidiVST ctor(). How to pass
    # Engine instance without circ ref?
    # :TODO 2.Name (1st arg) should come directly from how variable is named
    # (.nameof())
    serum_processor = render_engine.make_plugin_processor("serum",
                                                          song_data.synth_path)
    serum_processor.load_preset(serum.preset_path)
    serum_processor.load_midi(serum.midi_path, beats=True)

    render_engine.build_graph(serum_processor)

    render_engine.render_to_file(song_data)


if __name__ == '__main__':
    sys.exit(main())
