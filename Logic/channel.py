from logger import logger_channel
from MidiVST import VST


class channel():

    def __init__(self, style_data):
        self.channel_name = style_data['channel_name']
        self.construct(style_data['plugins'])

    def get_tuples(self):
        logger_channel.info('Tuple is creating')

    def construct(self, plugins):
        for plug_conf in plugins:
            # add, to the attributes
            VST(plug_conf)
        return None
