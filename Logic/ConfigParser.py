import json
# import logging
from os.path import isfile
# import os
from pathlib import Path  # much more usefull, then os
import shutil
from uuid import uuid4

from pretty_midi import pretty_midi

from SongData import SongData
from Exceptions import JsonError, JsonNotFoundError
from logger import logger_conf


class StyleConfig:
    """
        Class for the StyleConfiguration (just for one being used).
    """
    def __init__(self, d):
        self.__dict__ = d


class SongConfig:
    """
        Class for the Song Configuration (just for one being used).
    """
    def __init__(self, d):
        self.__dict__ = d
    # here will be special methods to process the params, like the length check

    def create_midi_duplicate_bpm(self, bpm):
        """
        Logic: if the bpm is presented in a style configuration, there should x
        be a self.bpm with a value (None in other case).

        To change the bpm midi file should be changed, so there is a need to
        save a copy of a midi file without changing the initial one.

        To add simplicity and provide the same workflow for all the cases, all
        midi file will be duplicated in a ./tmp folder of a project (with the
        same relative path.
        """
        if not bpm:
            pass

        else:
            pass
        return True

    def duplicate_midi_tmp(self):
        """
        Creates copy of the song in ./tmp folder
        """
        self.tmp_path = Path('.') / 'tmp' / 'midi'
        for track in self.Tracks:
            new_name = str(uuid4()) + '.mid'
            tmp_midi_path = self.tmp_path / new_name
            print(Path('.').absolute())
            print(tmp_midi_path.absolute())
            shutil.copy(track['midi_path'], tmp_midi_path.absolute())
            logger_conf.debug(f'{track["midi_path"]} copied into '
                              f'{str(self.tmp_path)} as '
                              f'{new_name}')
            track['tmp_midi_path'] = tmp_midi_path.absolute()

    def change_bpm(self):
        return True


class ConfigParser:
    """
    This object consumes the json files and creates requiered song and style
    config objects.

    *** There were old version, which is not used right not, but during the
    development we had to save previous functionality.
    """
    def __init__(self, separate=True):
        # if separate -> two configs with style and midi
        self.separate = separate
        self.song_config_version = 0
        self.song_data_struct = 'json'
        self.style_data_struct = 'json'
        self.config_path = Path('.') / 'Resources' / 'Configs'
        # :TODO change to env
        self.default_song_config = self.config_path / 'DemoSongsConfig.json'
        self.default_style_config = self.config_path / 'CompStylesConfig.json'
        self.style = "OrcheTrack"  # OrcheTrack/PianoTrack
        self.song = "7_Rings"  # 7_Rings/Bruno
        logger_conf.debug('current path for config is: '
                          f'{str(self.config_path.absolute())}')

    def build_midi_data(self, song=None):
        """
        Consumes the Json config from the file, which is stored in attribute.
        :return: SongConfig object of a chosen (in attribute) song.
        """
        print(type(self))
        if song:
            self.song = song

        check_json(self.default_song_config)
        with open(self.default_song_config, 'r') as js:
            data = json.load(js)
        song = SongConfig(data[self.song])  # we read only one song's data
        logger_conf.info(f'{self.style} is used')
        return song

    def build_style_data(self, style=None):
        """
        Consumes the Json config from the file, which is stored in attribute.
        :return: StyleConfig object of a chosen (in attribute) style.
        """
        if style:
            self.style = style

        check_json(self.default_style_config)
        with open(self.default_style_config, 'r') as js:
            data = json.load(js)
        style = StyleConfig(data[self.style])
        logger_conf.info(f'{self.song} is used')
        return style

    def build_song_data(self, style='HousetrackDemo'):
        """
        Parses SongsConfig.json for information about genre chosen,
        instruments and other information.

        TO NIKITA: The functionality is the same, but instead of previously
        used 'self' 'style' parameter is used
        """
        if self.separate:  # this can be estimated as a mark of new version
            style = self.build_style_data()
            midi = self.build_midi_data()
            return style, midi

        config_path = './Logic/SongsConfig.json'

        if isfile(config_path) is None:
            logger_conf.error('Config file not found!')
            raise JsonNotFoundError
        else:
            logger_conf.debug('Config file exists.')

        with open(config_path) as json_file:
            # :TODO Add Serialization as a class object?
            # :TODO Add checks for JSON structure, values. Add an exception
            #  raising.
            logger_conf.info(f'{style=}')
            if json_file is None:
                logger_conf.error(f'Config {config_path} is empty')
                raise JsonError
            data = json.load(json_file)
            logger_conf.debug('Configuration is loaded.')
            song_data = SongData()
            logger_conf.debug('Reading config file...')
            if data["OutputPath"] is not None:
                song_data.output_path = data["OutputPath"]
            else:
                logger_conf.warning('No output path')
                song_data.output_path = '.'

            song_data.bpm = float(data["BPM"])
            song_data.length = float(data["SongLengthInSeconds"])
            logger_conf.debug(data)
            logger_conf.info(data[style])
            logger_conf.info(f'OutputPath: {song_data.output_path}')
            logger_conf.debug(f'BPM: {song_data.bpm}')
            logger_conf.debug(f'SongLengthInSeconds: {song_data.length}')
            # :TODO RIGHT NOW only the latest instrument for the genre is
            #  being loaded. Get rif of the loop.
            for i in data[style]:
                song_data.synth_path = i['synthPath']
                song_data.preset_path = i['fxpPresetPath']
                song_data.midi_path = i['midiPath']

                song_data.length = get_length_to_render(song_data)
                # TODO print in color
                logger_conf.info(f'synthPath: {song_data.synth_path}')
                logger_conf.info(f'fxpPresetPath: {song_data.preset_path}')
                logger_conf.info(f'midiPath: {song_data.midi_path}')

            return song_data


def check_json(path: Path):

    if not isfile(path):
        logger_conf.error(f'Config file {str(path)} not found!')
        raise JsonNotFoundError
    else:
        logger_conf.debug(f'Config file {str(path)} exists.')


def get_length_to_render(song_data: SongData):
    if song_data.length is None:
        midi_data = pretty_midi.PrettyMIDI(song_data.midi_path)
        logger_conf.info(f'midi conf loaded from {song_data.midi_path}')
        return midi_data.instruments[0].get_end_time()
    else:
        logger_conf.warning(f'end time not found, length: {song_data.length}')
        return song_data.length
