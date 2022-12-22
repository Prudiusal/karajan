import json
# import logging
from os.path import isfile
from pathlib import Path  # much more usefull, then os

from pretty_midi import pretty_midi

from SongData import SongData
from Exceptions import JsonError, JsonNotFoundError
from logger import logger_conf


class StyleConfig:
    def __init__(self, d):
        self.__dict__ = d
    # :TODO __repr__, __str__, __slots__


class SongConfig:
    def __init__(self, d):
        self.__dict__ = d
    # here will be special methods to process the params, like the length check


class ConfigParser:
    def __init__(self, separate=False):
        # if separate -> two configs with style and midi
        self.separate = separate
        self.song_config_version = 0
        self.song_data_struct = 'json'
        self.style_data_struct = 'json'
        self.config_path = Path('.') / 'Resources' / 'Configs'
        # :TODO change to env
        self.default_song_config = self.config_path / 'TestSongsConfig.json'
        self.default_style_config = self.config_path / 'TestStylesConfig.json'
        # :TODO change to env
        self.style = "HouseTrackDemo"
        self.song = "SongOne"
        logger_conf.debug('current path for config is: '
                          f'{str(self.config_path.absolute())}')

    def build_midi_data(self):
        check_json(self.default_song_config)
        with open(self.default_song_config, 'r') as js:
            data = json.load(js)
        song = SongConfig(data[self.song])  # we read only one song's data
        logger_conf.info(f'{self.style} is used')
        return song

    def build_style_data(self):
        check_json(self.default_style_config)
        with open(self.default_style_config, 'r') as js:
            data = json.load(js)
        style = StyleConfig(data[self.style])
        logger_conf.info(f'{self.song} is used')
        return style

    # def build_song_data(self: str = 'HousetrackDemo'):
    # @staticmethod
    # def build_song_data(style='HousetrackDemo'):
    def build_song_data(self, style='HousetrackDemo'):
        """
        Parses SongsConfig.json for information about genre chosen,
        instruments and other information.

        TO NIKITA: The functionality is the same, but instead of previosly
        used 'self' 'style' parameter is used
        """
        if self.separate:
            style = self.build_style_data()
            midi = self.build_midi_data()
            return style, midi

        # print(self)
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
    # :TODO add other cases from the notes
    # :TODO change to pathlib.Path methods
    if isfile(path) is None:
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
