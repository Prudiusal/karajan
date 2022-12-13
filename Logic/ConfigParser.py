import json
from os.path import isfile

from pretty_midi import pretty_midi

from SongData import SongData


class ConfigParser:
    def build_song_data(self: str = 'HousetrackDemo'):
        """
        Parses SongsConfig.json for information about genre chosen,
        instruments and other information.
        """
        config_path = 'SongsConfig.json'

        if isfile(config_path) is None:
            raise FileNotFoundError

        with open(config_path) as json_file:
            # :TODO Add Serialization as a class object?
            # :TODO Add checks for JSON structure, values. Add an exception raising.
            assert json_file is not None, 'Config is empty'
            data = json.load(json_file)

            song_data = SongData();
            print("Reading config file...")

            song_data.output_path = data["OutputPath"] if data["OutputPath"] is not None else './'
            song_data.bpm = float(data["BPM"])
            song_data.length = float(data["SongLengthInSeconds"])

            print("outputPath:", song_data.output_path)
            print("BPM:", song_data.bpm)
            print("SongLengthInSeconds:", song_data.length)

            print(data[self])
            # :TODO RIGHT NOW only the latest instrument for the genre is being loaded. Get rif of the loop.
            for i in data[self]:
                song_data.synth_path = i['synthPath'];
                song_data.preset_path = i['fxpPresetPath'];
                song_data.midi_path = i['midiPath'];

                song_data.length = get_length_to_render(song_data)

                # TODO print in color
                print("synthPath:", song_data.synth_path)
                print("fxpPresetPath:", song_data.preset_path)
                print("midiPath:", song_data.midi_path)
                print()

            return song_data;


def get_length_to_render(song_data: SongData):
    if song_data.length is None:
        midi_data = pretty_midi.PrettyMIDI(song_data.midi_path)
        return midi_data.instruments[0].get_end_time()
    else:
        return song_data.length
