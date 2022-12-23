from logger import logger_track
from MidiVST import VST


class Track():

    def __init__(self, style_data):
        self.track_name = style_data['track_name']
        self.plugins_data = style_data['plugins']
        self.plugins = []
        self.tuples_track = []
        self.track_output_plug_name = None

    def get_tuples(self):
        logger_track.info('Tuple is creating')

    def construct(self, func):
        # :TODO set the automatic method extraction
        for plug_conf in self.plugins_data:
            # add, to the attribute
            # plugin_name = plug_conf['synthName']
            self.plugins.append(VST(func, plug_conf, self.track_name))
        return None

    def get_track_tuples(self):
        if self.tuples_track:
            return self.tuples_track
        for plug in self.plugins:
            if not self.tuples_track:  # fot the first element
                self.tuples_track.append((plug.plugin, []))
                input_to_next_plugin = plug.plugin_name_global
            else:
                self.tuples_track.append((plug.plugin,
                                            [input_to_next_plugin]))
                input_to_next_plugin = plug.plugin_name_global
        self.track_output_plug_name = input_to_next_plugin
        logger_track.info(self.tuples_track)
        logger_track.info(self.track_output_plug_name)
        return self.tuples_track, self.track_output_plug_name
