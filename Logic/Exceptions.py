class SynthesisError(Exception):
    # print("SynthesisError has occurred.")
    # :TODO pass VST parameters to the logs
    pass


class PluginError(Exception):
    pass


class JsonError(Exception):
    pass


class JsonNotFoundError(JsonError):
    pass


def validate_plugin_path(path):
    if not path.is_file():
        raise PluginNotFoundError(path.absolute())


class SongNotFoundError(JsonError):
    pass


class WrongJsonFormatError(Exception):
    pass


class StyleNotFoundError(JsonError):
    pass


class WrongStyleType(TypeError):
    pass


class WrongStyleFormat(ValueError):
    pass


class StyleNameError(WrongStyleFormat):
    pass


class StyleConfigError(TypeError):
    pass


class NoStyleNameError(WrongStyleFormat):
    pass


class StyleTracksConfigError(WrongStyleFormat):
    pass


class StyleTrackFormatError(TypeError):
    pass


class PluginConfigError(Exception):
    pass


class WrongDawDreamerProcessor(Exception):
    pass


class DSPNotFoundError(FileNotFoundError):
    pass


class PluginNotFoundError(FileNotFoundError):
    pass


class PresetNotFoundError(FileNotFoundError):
    pass


class TrackFinalFaustProcessorError(Exception):
    pass
