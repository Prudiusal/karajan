import json
# import logging
from os.path import isfile
# import os
from pathlib import Path  # much more usefull, then os
import shutil
from uuid import uuid4
from itertools import groupby

# from pretty_midi import pretty_midi
from mido import MidiFile, bpm2tempo, tempo2bpm, MetaMessage

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

    def calculate_length(self):
        bpm = self.__dict__.get('BPM', 120)
        if bpm == 120:
            logger_conf.info('Standart bmp 120 is used')
            self.BPM = 120
        else:
            logger_conf.info(f'Bmp {self.BPM} is used')
        times = []
        # TODO: change to the max of all the files except the Drums
        for track in self.Tracks:
            path = track.get('tmp_midi_path', track.get('midi_path'))
            try:
                mid = MidiFile(str(path))
            except Exception as e:
                logger_conf.error(e)
                continue
            times.append(mid.length)
        length = min(times)
        k = 120 / bpm  # default tempo corresponds to bpm=120
        return k * length

    def delete_tempo_msgs(self):
        for song_track in self.Tracks:
            midi_file = song_track['tmp_midi_path']
            mid = MidiFile(midi_file)
            for i, track in enumerate(mid.tracks):
                track_filtered = [msg for msg in track
                                  if msg.type != 'set_tempo']
                mid.tracks[i] = track_filtered
            mid.save(midi_file)

    def duplicate_midi_tmp(self):
        """
        Creates copy of the song in ./tmp folder
        This allows to change the midi files while 
        the processing, without changing the original file
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

    def set_length_attribute(self):
        """NOT USED"""
        times = []
        for track in self.Tracks:
            path = track.get('tmp_midi_path', track.get('midi_path'))
            try:
                mid = MidiFile(str(path))
            except Exception as e:
                logger_conf.error(e)
                logger_conf.info('length of 100 seconds is used')
                times.append(100)
                continue
            times.append(mid.length)
        self.Length = min(times)
        return True

    def set_or_validate_bpm(self, bpm):
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
            return False
            self.get_bpm()
            logger_conf.info(f'Initial bpm is {self.bpm}')
            return True
        else:
            return False
            self.change_bpm(bpm)
            logger_conf.info(f'Changed bpm is {self.bpm}')
            return True

    def change_bpm(self, bpm):
        logger_conf.debug(f'bpm is changing to {bpm}')
        for track in self.Tracks:
            midi_file_path = track['tmp_midi_path']
            self.change_bpm_midifile(midi_file_path, bpm)
            # TODO: probably unchanged midi track shold be removed
        self.bpm = bpm
        return True

    def change_bpm_midifile(self, filename, bpm):
        try:
            mid = MidiFile(filename)
        except Exception as e:
            logger_conf.error(e)
        tempo = bpm2tempo(bpm)
        if not self.change_tempo(mid, tempo):  # 'Tempo haven\'t changed'
            self.add_set_tempo_msg(mid, bpm)
        mid.save(filename)
        return True

    @staticmethod
    def add_set_tempo_msg(mid, bpm):
        set_tempo_msg = MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0)
        mid.tracks[0].append(set_tempo_msg)

    @staticmethod
    def change_tempo(mid, new_tempo):
        flag = False
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    msg.tempo = new_tempo
                    flag = True
        return flag

    def get_bpm(self):
        logger_conf.debug('Getting the bpm')
        bpms = []
        for track in self.Tracks:
            midi_file_path = track['tmp_midi_path']
            bpm = self.get_bpm_midifile(midi_file_path)
            if bpm:
                bpms.append(bpm)
                # TODO: probably unchanged midi track shold be removed
        if not bpms:
            logger_conf.debug('No bpm found for the mid')
            logger_conf.debug('Default bpm 120 is used')
            self.bpm = 120
            return True
        elif all_equal(bpms):
            self.bpm = bpm
            return True

    @staticmethod
    def get_bpm_midifile(filename):
        try:
            mid = MidiFile(filename)
        except Exception as e:
            logger_conf.error(e)
        tempos = []
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempos.append(msg.tempo)
        if not tempos:
            return 120
        elif all_equal(tempos):
            return tempo2bpm(tempos[0])
        elif not all_equal(tempos):
            # TODO: if has not changed -> create message or delete midi
            # self.change_tempo(mid, tempo2bpm(tempos[0]))
            mid.save(filename)
            return tempo2bpm(tempos[0])


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


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

                # song_data.length = get_length_to_render(song_data)
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


# def get_length_to_render(song_data: SongData):
#     if song_data.length is None:
#         midi_data = pretty_midi.PrettyMIDI(song_data.midi_path)
#         logger_conf.info(f'midi conf loaded from {song_data.midi_path}')
#         return midi_data.instruments[0].get_end_time()
#     else:
#         logger_conf.warning(f'end time not found, length:{song_data.length}')
#         return song_data.length
