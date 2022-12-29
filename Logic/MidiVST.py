# from dawdreamer import PluginProcessor

from logger import logger_VST


class Vst_adder:
    def init__(self, kwargs):
        print(type(kwargs))
        for k in kwargs:
            print(k)
        # super().__init__()

def processor_configured(func, config, track_name):
    plugin_name = config['pluginName']
    plugin_path = config['pluginPath']
    preset_path = config['fxpPresetPath']
    plugin_name_global = f'{track_name}_{plugin_name}'
    processor = func(plugin_name_global, plugin_path)
    logger_VST.debug(preset_path)
    processor.load_preset(preset_path)  # can be called in function
    logger_VST.info(f'Uses {processor.get_num_output_channels()}'
                    ' output channels.')
    return processor

class VST:
    """Class creates the plugin processor with custom parameters
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
