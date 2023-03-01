# from dawdreamer import PluginProcessor

from logger import logger_VST


def delay_creator(func, config, global_name):
    """
    This functions covers creation of the Delay processors and initial
    setup for it.
    """
    logger_VST.error('Delay creator not implemented!')
    pass


def faust_creator(func, config, global_name):
    """
    This functions covers creation of the Faust processors and initial
    setup for it.
    """
    # TODO: convert to '.get' with default to handle the errors of JSON
    logger_VST.debug('FAUST IS CREATING')
    dsp_path = config['dspPath']
    logger_VST.debug(f'{global_name=}')
    logger_VST.debug(f'{dsp_path=}')
    # TODO: check for files, etc...
    processor = func(global_name)
    processor.set_dsp(dsp_path)
    processor.compile()
    assert(processor.compiled)
    return processor


def vst_creator(func, config, global_name):
    """
    This functions covers creation of the VST processors and initial
    setup for it.
    """
    plugin_path = config['pluginPath']
    preset_path = config['fxpPresetPath']
    logger_VST.debug(f'{global_name=}')
    logger_VST.debug(f'{plugin_path=}')
    logger_VST.debug(f'{preset_path=}')
    # TODO: check for files, etc...
    processor = func(global_name, plugin_path)
    processor.load_preset(preset_path)  # can be called in function
    # make sure the plugin name in CopmStylesConfig contains 'XO'
    # json: "PianoDrums['Tracks'][idx_of_track]['plugin_name'] = 'XO'
    if 'XO' in global_name:
        logger_VST.debug(processor.get_parameters_description())
        index = 0  # index of parameter to change
        value = 'new_value_of_parameter'  # probably will be BPM
        processor.set_parameter(index, value)
    if 'ezk' in global_name.lower():
        processor.open_editor()
    return processor


def processor_creator(func, config, track_name):
    """
    With configuration from Json creates the plugins for one track
    :param func: method of RenderEngine, which creates the processor
    :param config: config for the one processor (VST)
    :param track_name: track to which processor refers to.
    :return: instance of dawdreamer.processor class.

    """
    # TODO: make it able to choose init in accordance with proc type
    processor_type = config.get('type', 'vst')
    processor_name = config['pluginName']
    name_global = f'{track_name}_{processor_name}'

    if processor_type == 'faust':
        return faust_creator(func, config, name_global)
    elif processor_type == 'vst':
        return vst_creator(func, config, name_global)
    else:
        logger_VST.waring(f'Unknown type: {processor_type} for '
                          f'{processor_name}')
        return False


class VST:
    """
    not used right now!

    Class creates the plugin processor with custom parameters
    (index, track, midi=T/F, path to the plugin, path to the preset)
    """
    def __init__(self, func, config, track_name):
        self.index = config['index']
        self.plugin_name = config['pluginName']  # same in default
        self.preset_path = config['fxpPresetPath']  # useless
        self.track_name = track_name  # used only with __init__
        self.plugin_name_global = f'{self.track_name}_{self.plugin_name}'

        self.plugin = func(self.plugin_name_global, self.plugin_path)
        logger_VST.debug(self.preset_path)
        self.plugin.load_preset(self.preset_path)  # can be called in function
        logger_VST.info(f'Uses {self.plugin.get_num_output_channels()}'
                        ' output channels.')

        if self.plugin_name == 'ad2':
            logger_VST.info('AD2 plugin is used')
            logger_VST.info(f'AD2 uses {self.plugin.get_num_output_channels()}'
                            ' output channels.')
            logger_VST.info(f'AD2 uses {self.plugin.get_num_input_channels()}'
                            ' input channels.')
            # print(self.plugin.get_plugin_parameters_description())
            # self.plugin.set_bus(0, 1)
            logger_VST.info(f'AD2 uses {self.plugin.get_num_output_channels()}'
                            ' output channels.')
            logger_VST.info(f'AD2 uses {self.plugin.get_num_input_channels()}'
                            ' input channels.')


class MidiVST:

    def __init__(self, plugin_path, preset_path, midi_path) -> None:
        """
        Class which represents MidiVST plugin object. Contains properties
        parsed from SongConfig.json

        Args:
            plugin_path (Path): Path to the VST .component file
            (usually under /Library/Audio/Plug-Ins/Components/ on OSX)
            preset_path (Path): Path to the VST preset .fxp file
            midi_path (Path): Path to the midi file

        Methods:
            __init__(): property initialization
            _init_synth(self):
        """
        self.plugin_path = plugin_path
        self.preset_path = preset_path
        self.midi_path = midi_path
        logger_VST.debug('midiVST initialized')
        # for midi_file in tqdm(self.filelist):
        #     try:
        #         self.process_midi(midi_file)
        #     except Exception as e:
        #         print(e)
        #         continue


# class SerumSynth(MidiVST):
#     # :TODO Add autodeterming from the config if it's the Serum synth
#     def __init__(self, preset_path, output_path=None, sr=44100,
#                   buffer_size=128) -> None:
#         assert '.fxp' in preset_path, 'synth_plugin must point to .fxp file'
#         synth_plugin = "C:/Program Files/Steinberg/VSTPlugins/Serum_x64.dll"
#         super().__init__(synth_plugin, preset_path, output_path,
#                           sr, buffer_size)
#         return self.render_engine.make_plugin_processor("Synth",
#                                                           self.plugin_path)


# class KontaktSynth(MidiVST):
#     def __init__(self, synth_preset) -> None:
#         assert '.nkm' in synth_preset, 'synth_plugin must point to
#                                                       .nkm file'
#         synth_plugin = "/Library/Audio/Plug-Ins/Components/Kontakt.component"
#         super().__init__(synth_plugin, synth_preset, midi_path)
#
#     def _init_synth(self):
#         self.copy_and_rename_def()
#
#     def copy_and_rename_def(self,
#                             default_dir='/Users/%Username%/Library/
#                             Application Support/Native Instruments/Kontakt
#                               /default'):
#         """
#         Workaround to load a Kontatk synth : we replace the default Kontakt
#           synth so it will be loaded by default when initializing Kontakt
#         :param default_dir: path to default kontakt directory
#         """
#         src_path = self.synth_preset
#         # The file has to be renamed
#         temp_path = os.path.join(os.path.dirname(self.synth_preset),
#                                   'kontakt_def.nkm')
#         shutil.copy(src_path, temp_path)
#         shutil.copy(temp_path, default_dir)
