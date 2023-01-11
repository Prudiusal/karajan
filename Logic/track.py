from collections import OrderedDict

from logger import logger_track
from MidiVST import processor_creator


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
        self.processors = OrderedDict()
        self.sidechains = OrderedDict()  # processor: [chain1, chain2, ... ]
        self.tuples_track = []
        self.track_output_name = self.track_name  # to have default output name

    def construct(self):
        """
        Creates the instances of plugins and other processors

        TODO:
            1. Creation of FAUST processors
            2. Sidechain case for the FAUST/VST
            3. Rename plugins -> processors in JSON
            4. Add 'type' to the JSON (vst/faust)
            5. If processor is not created -> ignore him
            6. If synth is not created -> ignore channel
        """
        for processor_conf in self.plugins_data:
            processor_name = processor_conf['pluginName']
            processor_type = processor_conf.get('type', 'vst')
            logger_track.debug(f'{processor_type =}')

            f = self.proc_funcs.get(processor_type)
            # TODO: convert to method (to use with Ad2 etc)
            new_proc = processor_creator(f, processor_conf, self.track_name)
            if new_proc:  # error during creation may occur, so will be False
                self.processors[processor_name] = new_proc
            else:
                logger_track.warning(f'Processor {processor_name} not created')
                if not len(self.processors):
                    logger_track.error(f'Track {self.track} name has no synth'
                                       ' and its will not be used')
                    # TODO: exit it synth is not created, handle the midi
                    # loading
                continue

            if processor_name == 'ad2':  # this plugin requires summation
                logger_track.info('Addictive drum 2 is used')
                adder_func = self.proc_funcs.get('add')
                self.processors['ad2_adder'] = adder_func('ad2_adder',
                                                          24 * [1])

            if processor_conf.get('sideChain'):
                logger_track.info('SideChain from'
                                  f'{processor_conf.get("sideChain")} is used')
                self.sidechains[processor_name] = \
                    processor_conf.get("sideChain")
        # to use by sidechain. Output processor will have a default name
        # TODO: cover with function
        final_proc_func = self.proc_funcs.get('faust')
        final_proc = final_proc_func(self.track_name)
        final_proc.set_dsp_string('process = _, _;')
        final_proc.compile()
        assert(final_proc.compiled)
        self.processors['final'] = final_proc
        assert self.processors['final'].get_name() == self.track_name
        logger_track.debug('output proc name is '
                           f'{self.processors["final"].get_name()} for '
                           f'{self.track_name}')

    def get_track_tuples(self):
        """Here we have to use the instances inside the track to combine
        the graph of tuples. Each object should have an attribute 'processor'
        (right now its named as a plugin)
        """
        previous_processor = None
        for processor in self.processors.values():
            """
            Check the sidechain, configure the input
            """
            inputs = []
            if previous_processor:
                inputs.append(previous_processor)
            if self.sidechains.get(processor):
                inputs.extend(self.sidechains.get(processor))
                logger_track.info(f'sidechain input: {inputs}')
            self.check_inputs(inputs)
            # TODO: assert for the processor type
            self.tuples_track.append((processor, inputs))
            previous_processor = processor.get_name()
        logger_track.debug(self.tuples_track)
        return self.tuples_track, self.track_output_name

    @staticmethod
    def check_inputs(proc_names_list):
        for proc_name in proc_names_list:
            assert type(proc_name) == str, 'Should be string'
