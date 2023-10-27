from Exceptions import (
    NoStyleNameError,
    PluginConfigError,
    StyleNameError,
    StyleTracksConfigError,
    WrongJsonFormatError,
)


class StyleConfig:
    """
    Class for the StyleConfiguration (just for one being used).
    """

    def __init__(self, d):
        """
        The function initializes an object with attributes based on a
        dictionary input.
        Object will have the same attributes as keys in dictionary.

        :param d: The parameter `d` is expected to be a dictionary.
        It is used to initialize the attributes `name` and `tracks` of the
        object. If `d` is not a dictionary, it raises a `WrongJsonFormatError`
        exception. The `__dict__` attribute of the object
        """
        self.name = None
        self.tracks = None
        if not isinstance(d, dict):
            raise WrongJsonFormatError
        self.__dict__ = d

    def validate(self):
        """
        The function `validate` checks if an StyleConfig has the required
        attributes and their corresponding types, and raises specific errors
        if any of the checks fail.
        :return: a boolean value of True.
        """
        if not hasattr(self, "name"):
            raise NoStyleNameError
        if not isinstance(self.name, str):
            raise StyleNameError
        if not hasattr(self, "tracks"):
            raise StyleTracksConfigError
        if not isinstance(self.tracks, list):
            raise StyleTracksConfigError
        for track in self.tracks:
            if not isinstance(track, dict):
                raise StyleTracksConfigError
            if not track.get("track_name"):
                raise StyleTracksConfigError
            if not track.get("plugins"):
                raise StyleTracksConfigError

            plugins = track["plugins"]

            if not isinstance(plugins, list):
                raise PluginConfigError

            for plug in plugins:
                if not plug.get("pluginName"):
                    raise PluginConfigError
        return True
