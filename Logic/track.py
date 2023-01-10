from collections import OrderedDict

from logger import logger_track
from MidiVST import processor_configurator


class Track:
    """
    Contains all the plugins for one line of the processing.
    Stores the plugins and other processors.
    """

    def __init__(self, style_data, proc_funcs):
        """
        :param style_data: explains the track
        (drums, pads, lead etc)
        :param plugin_func: renderEngine method to create VST
        :param adder_func: renderEngine method to create adder
        """
        self.track_name = style_data['track_name']
        self.plugins_data = style_data['plugins']
        self.proc_funcs = proc_funcs
        # self.plugin_func = plugin_func
        # self.adder_func = adder_func
        # self.faust_func = faust_func
        self.processors = OrderedDict()
        self.sidechains = OrderedDict()
        self.tuples_track = []
        self.track_output_name = None

    def get_output_name(self):
        """Returns the global name of last plugin in track"""
        pass
        if self.track_output_name:
            return self.track_output_name
        else:
            self.track_output_name = None

    def construct(self):
        """
        Creates the instances of plugins and other processors

        TODO:
            1. Creation of FAUST processors
            2. Sidechain case for the FAUST/VST
            3. Rename plugins -> processors
            4. Add 'type' to the JSON (vst/faust)
        """
        for processor_conf in self.plugins_data:
            processor_name = processor_conf['pluginName']
            processor_type = processor_conf.get(['type'], 'vst')

            # case - switch for the functions to create
            f = self.proc_funcs.get(processor_type)

            # TODO: make it able to choose init in accordance with config
            # (VST, Faust, ...)
            self.processors[processor_name] = \
                processor_configurator(f, processor_conf,
                                       self.track_name)

            if processor_name == 'ad2':  # this plugin requires summation
                logger_track.info('Addictive drum 2 is used')
                adder_func = self.proc_funcs.get('add')
                self.processors['ad2_adder'] = adder_func('ad2_adder', 24 * [1])

            if processor_conf.get('sideChain'):
                logger_track.info(f'SideChain from {processor_conf.get("sideChain")} is used.')
                self.sidechains[processor_name] = processor_conf.get("sideChain_from")


    def get_track_tuples(self):
        """Here we have to use the instances inside the track to combine
        the graph of tuples. Each object should have an attribute 'processor'
        (right now its named as a plugin)
        """
        previous_processor = None

        for processor in self.processors.values():
            if not self.tuples_track:  # for the first element we add instance
                self.tuples_track.append((processor, []))
                previous_processor = processor.get_name()  #
            else:
                self.tuples_track.append((processor,
                                          [previous_processor]))
                previous_processor = processor.get_name()
                # previous_processor = vst.plugin_name_global
        self.track_output_name = previous_processor
        logger_track.debug(self.tuples_track)
        logger_track.debug(self.track_output_name)
        return self.tuples_track, self.track_output_name
