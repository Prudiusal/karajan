from collections import OrderedDict

from logger import logger_track
from MidiVST import processor_configured


class Track():

    def __init__(self, style_data, plugin_func, adder_func):
        self.track_name = style_data['track_name']
        self.plugins_data = style_data['plugins']
        self.plugin_func = plugin_func
        self.adder_func = adder_func
        self.processors = OrderedDict()
        self.tuples_track = []
        self.track_output_plug_name = None

    def get_tuples(self):
        logger_track.info('Tuple is creating')

    def construct(self):
        # :TODO set the automatic method extraction
        for plug_conf in self.plugins_data:
            # add, to the attribute
            plugin_name = plug_conf['pluginName']
            self.processors[plugin_name] = processor_configured(
                self.plugin_func, plug_conf, self.track_name)
            if plugin_name == 'ad2':
                logger_track.info('Addictive drum 2 is used')
                self.processors['ad2_adder'] = self.adder_func('ad2_adder',
                                                               24*[1])
        return None

    def get_track_tuples(self):
        """Here we have to use the instances inside the track to combine
        the graph of tuples. Each object should have an attribute 'processor'
        (right now its named as a plugin)
        """
        previous_processor = None
        # if self.tuples_track:
        #     return self.tuples_track
        # for plug in iter(self.plugins):
        for processor in self.processors.values():
            if not self.tuples_track:  # fot the first element we add instance
                self.tuples_track.append((processor, []))
                # previous_processor = plug.plugin_name_global  #
                previous_processor = processor.get_name()  #
            else:
                self.tuples_track.append((processor,
                                          [previous_processor]))
                previous_processor = processor.get_name()
                # previous_processor = vst.plugin_name_global
        self.track_output_plug_name = previous_processor
        logger_track.info(self.tuples_track)
        logger_track.info(self.track_output_plug_name)
        return self.tuples_track, self.track_output_plug_name
