class MidiVST:
    def __init__(self, plugin_path, preset_path, midi_path) -> None:
        """
        Class which represents MidiVST plugin object. Contains properties parsed from SongConfig.json

        Args:
            plugin_path (Path): Path to the VST .component file (usually under /Library/Audio/Plug-Ins/Components/ on OSX)
            preset_path (Path): Path to the VST preset .fxp file
            midi_path (Path): Path to the midi file

        Methods:
            __init__(): property initialization
            _init_synth(self): 
        """
        self.plugin_path = plugin_path
        self.preset_path = preset_path
        self.midi_path = midi_path

        # for midi_file in tqdm(self.filelist):
        #     try:
        #         self.process_midi(midi_file)
        #     except Exception as e:
        #         print(e)
        #         continue

# class SerumSynth(MidiVST):
#     # :TODO Add autodeterming from the config if it's the Serum synth
#     def __init__(self, preset_path, output_path=None, sr=44100, buffer_size=128) -> None:
#         assert '.fxp' in preset_path, 'synth_plugin must point to a .fxp file'
#         synth_plugin = "C:/Program Files/Steinberg/VSTPlugins/Serum_x64.dll"
#         super().__init__(synth_plugin, preset_path, output_path, sr, buffer_size)
#         return self.render_engine.make_plugin_processor("Synth", self.plugin_path)


# class KontaktSynth(MidiVST):
#     def __init__(self, synth_preset) -> None:
#         assert '.nkm' in synth_preset, 'synth_plugin must point to a .nkm file'
#         synth_plugin = "/Library/Audio/Plug-Ins/Components/Kontakt.component"
#         super().__init__(synth_plugin, synth_preset, midi_path)
#
#     def _init_synth(self):
#         self.copy_and_rename_def()
#
#     def copy_and_rename_def(self,
#                             default_dir='/Users/%Username%/Library/Application Support/Native Instruments/Kontakt/default'):
#         """
#         Workaround to load a Kontatk synth : we replace the default Kontakt synth so it will be loaded by default when initializing Kontakt
#         :param default_dir: path to default kontakt directory
#         """
#         src_path = self.synth_preset
#         # The file has to be renamed
#         temp_path = os.path.join(os.path.dirname(self.synth_preset), 'kontakt_def.nkm')
#         shutil.copy(src_path, temp_path)
#         shutil.copy(temp_path, default_dir)