class SynthesisError(Exception):
    print("SynthesisError has occurred.")
    # :TODO pass VST parameters to the logs
    pass


class PluginError(Exception):
    pass


class PluginNotFoundError(PluginError):
    pass


class JsonError(Exception):
    pass


class JsonNotFoundError(JsonError):
    pass


def validate_plugin_path(path):
    if not path.is_file():
        raise PluginNotFoundError(path.absolute())
