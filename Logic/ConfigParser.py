import json
# import logging
from os.path import isfile
from pathlib import Path  # much more usefull, then os

from pretty_midi import pretty_midi

from SongData import SongData
from Exceptions import JsonError, JsonNotFoundError
from logger import logger_conf


class ConfigParser:
    def __init__(self, separate=False):
        # if separate -> two configs with style and midi
        self.separate = separate
        self.song_config_version = 0
        self.song_data_struct = 'json'
        self.style_data_struct = 'json'
        self.config_path = Path('.')
        logger_conf.warning(f'current path is {str(self.config_path)}')

    def build_midi_data(self):
        pass

    def build_style_data(self):

        pass

    # def build_song_data(self: str = 'HousetrackDemo'):

    @staticmethod
    def build_song_data(style='HousetrackDemo'):
        """
        Parses SongsConfig.json for information about genre chosen,
        instruments and other information.
        """
        config_path = './Resources/Configs/SongsConfig.json'

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


def get_length_to_render(song_data: SongData):
    if song_data.length is None:
        midi_data = pretty_midi.PrettyMIDI(song_data.midi_path)
        logger_conf.info(f'midi conf loaded from {song_data.midi_path}')
        return midi_data.instruments[0].get_end_time()
    else:
        logger_conf.warning(f'end time not found, length: {song_data.length}')
        return song_data.length
