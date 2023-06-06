import unittest

from Logic.processor_creators import processor_creator, faust_creator, vst_creator
from Logic.processor_creators import check_plugin_path, check_preset_path, \
    check_dsp_path

from Logic import Track
from Logic import ConfigParser
from Logic import RenderEngine
from Logic import DSPNotFoundError, PresetNotFoundError, PluginNotFoundError
import settings as cfg
from helpers import cases
from dawdreamer.dawdreamer import PluginProcessor, AddProcessor, FaustProcessor


class TestSuite1(unittest.TestCase):
    def setUp(self):
        parser = ConfigParser()
        self.style_data = parser.build_style_data(cfg.STYLE)

        self.engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
        self.functions = {'vst': self.engine.make_plugin_processor,
                          'faust': self.engine.make_faust_processor,
                          'add': self.engine.make_add_processor}
        self.tracks = [Track(track_data, self.functions)
                       for track_data in self.style_data.tracks]

    def tearDown(self) -> None:
        del self.style_data
        del self.engine
        del self.functions
        del self.tracks



    def test_processor_creator_ok(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                processor_name = processor_conf['pluginName']
                processor_type = processor_conf.get('type', 'vst')
                f = track.proc_funcs.get(processor_type)
                new_proc = processor_creator(f, processor_conf, track.track_name)
                self.assertTrue(new_proc)
                self.assertIsInstance(new_proc, (PluginProcessor, AddProcessor,
                                                 FaustProcessor))

    def test_check_dsp_path(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                if processor_conf.get('type', 'vst') == 'faust':
                    path = processor_conf.get('dspPath')
                    check_dsp_path(path)
        with self.assertRaises(DSPNotFoundError):
            check_dsp_path('/bad/path')

    def test_check_plugin_path(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                if processor_conf.get('type', 'vst') == 'vst':
                    path = processor_conf.get('pluginPath')
                    check_plugin_path(path)
        with self.assertRaises(PluginNotFoundError):
            check_plugin_path('/bad/path')

    def test_check_preset_path(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                if processor_conf.get('type', 'vst') == 'vst':
                    path = processor_conf.get('fxpPresetPath')
                    check_preset_path(path)
        with self.assertRaises(PresetNotFoundError):
            check_preset_path('/bad/path')

    def test_faust_creator(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                processor_name = processor_conf['pluginName']
                processor_type = processor_conf.get('type', 'vst')
                name_global = f'{track.track_name}_{processor_name}'
                if processor_type == 'faust':
                    faust_creator(track.proc_funcs[processor_type],
                                  processor_conf, name_global)

    def test_vst_creator(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                processor_name = processor_conf['pluginName']
                processor_type = processor_conf.get('type', 'vst')
                name_global = f'{track.track_name}_{processor_name}'
                if processor_type == 'vst':
                    vst_creator(track.proc_funcs[processor_type],
                                  processor_conf, name_global)

