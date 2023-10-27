import json
from os.path import isfile
from pathlib import Path

# from SongData import SongData
from Exceptions import JsonNotFoundError, SongNotFoundError, StyleNotFoundError
from logger import logger_conf
from song_config import SongConfig
from style_config import StyleConfig

import settings as cfg


class ConfigParser:
    """
    This object consumes the json files and creates requiered song and style
    config objects.

    *** There were old version, which is not used right not, but during the
    development we had to save previous functionality.
    """

    def __init__(self):
        # self.song_config_version = 0
        self.song_data_struct = "json"
        self.style_data_struct = "json"

        self.default_style_config = cfg.STYLE_CONFIG_PATH
        self.style = "OrcheTrack"  # OrcheTrack/PianoTrack
        self.song = "7_Rings"  # 7_Rings/Bruno
        # logger_conf.debug('current path for config is: '
        #                   f'{str(self.config_path.absolute())}')
        logger_conf.debug(
            "current path for STYLE config is: " f"{self.default_style_config}"
        )

    def build_midi_data(self, song=None):
        """
        Consumes the Json config from the file, which is stored in attribute.
        :return: SongConfig object of a chosen (in attribute) song.
        """
        if song:
            self.song = song

        self.check_json(self.default_song_config)
        with open(self.default_song_config, "r") as js:
            data = json.load(js)
        if not data.get(self.song):
            raise SongNotFoundError
        song = SongConfig(data[self.song])  # we read only one song's data
        logger_conf.info(f"{self.style} is used")
        return song

    def build_style_data(self, style=None):
        """
        Consumes the Json config from the file, which is stored in attribute.
        :return: StyleConfig object of a chosen (in attribute) style.
        """
        if style:
            self.style = style
        else:
            logger_conf.warning(f"Default {self.style} is used")

        self.check_json(self.default_style_config)
        with open(self.default_style_config, "r") as js:
            data = json.load(js)
        if not data.get(self.style):
            raise StyleNotFoundError(self.style)
        style = StyleConfig(data[self.style])
        # style.validate()
        # logger_conf.info(f'{self.song} is used')
        return style

    @staticmethod
    def check_json(path: Path):
        """
        The function `check_json` checks if a JSON file exists at the given
        path and logs appropriate messages.

        :param path: The `path` parameter is the path to a JSON file that
        needs to be checked
        :type path: Path
        """
        if not isfile(path):
            logger_conf.error(f"Config file {str(path)} not found!")
            raise JsonNotFoundError
        else:
            logger_conf.debug(f"Config file {str(path)} exists.")
