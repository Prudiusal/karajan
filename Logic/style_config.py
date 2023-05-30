
from Exceptions import StyleNameError, NoStyleNameError, WrongJsonFormatError
from Exceptions import StyleTracksConfigError, PluginConfigError

class StyleConfig:
    """
        Class for the StyleConfiguration (just for one being used).
    """
    def __init__(self, d):
        if not isinstance(d, dict):
            raise WrongJsonFormatError
        self.__dict__ = d

    def validate(self):
        if not hasattr(self, 'name'):
            raise NoStyleNameError
        if not isinstance(self.name, str):
            raise StyleNameError
        if not hasattr(self, 'tracks'):
            raise StyleTracksConfigError
        if not isinstance(self.tracks, list):
            raise StyleTracksConfigError
        for track in self.tracks:
            if not isinstance(track, dict):
                raise StyleTracksConfigError
            if not track.get('track_name'):
                raise StyleTracksConfigError
            if not track.get('plugins'):
                raise StyleTracksConfigError
            plugins = track.get('plugins')

            if not isinstance(plugins, list):
                raise PluginConfigError

            for plug in plugins:
                if not plug.get('pluginName'):
                    raise PluginConfigError
