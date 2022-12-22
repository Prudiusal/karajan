from logger import logger_channel
from MidiVST import VST


class Channel():

    def __init__(self, style_data):
        self.channel_name = style_data['channel_name']
        self.plugins_data = style_data['plugins']
        self.plugins = []
        self.tuples_channel = []
        self.channel_output_plug_name = None

    def get_tuples(self):
        logger_channel.info('Tuple is creating')

    def construct(self, func):
        # :TODO set the automatic method extraction
        for plug_conf in self.plugins_data:
            # add, to the attributes
            # plugin_name = plug_conf['synthName']
            self.plugins.append(VST(func, plug_conf, self.channel_name))
        return None

    def get_channel_tuples(self):
        if self.tuples_channel:
            return self.tuples_channel
        for plug in self.plugins:
            if not self.tuples_channel:  # fot the first element
                self.tuples_channel.append((plug.plugin, []))
                input_to_next_plugin = plug.plugin_name_global
            else:
                self.tuples_channel.append((plug.plugin,
                                            [input_to_next_plugin]))
                input_to_next_plugin = plug.plugin_name_global
        self.channel_output_plug_name = input_to_next_plugin
        logger_channel.info(self.tuples_channel)
        logger_channel.info(self.channel_output_plug_name)
        return self.tuples_channel, self.channel_output_plug_name
