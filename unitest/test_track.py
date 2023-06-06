import unittest
from Logic import Track
from Logic import ConfigParser
from Logic import RenderEngine
from Logic import WrongDawDreamerProcessor, FaustProcessorNotFound
from copy import deepcopy
import helpers
from dawdreamer.dawdreamer import PluginProcessor, AddProcessor, FaustProcessor


from Logic.processor_creators import *

import settings as cfg
from helpers import cases


class TestSuite1(unittest.TestCase):
    def setUp(self):
        parser = ConfigParser()
        self.style_data = parser.build_style_data(cfg.STYLE)

        engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
        self.functions = {'vst': engine.make_plugin_processor,
                          'faust': engine.make_faust_processor,
                          'add': engine.make_add_processor}
        self.tracks = [Track(track_data, self.functions)
                       for track_data in self.style_data.tracks]
#
    def test_construct_ok(self):
        for track in self.tracks:
            track.construct()

    def test_construct_functions_bad(self):
        for track in self.tracks:
            for processor_conf in track.plugins_data:
                processor_conf['type'] = 'Bad_Type'
        for track in self.tracks:
            with self.assertRaises(WrongDawDreamerProcessor):
                track.construct()






class TestSuite2(unittest.TestCase):
    def setUp(self):
        parser = ConfigParser()
        self.style_data = parser.build_style_data(cfg.STYLE)

        engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
        self.functions = {'vst': engine.make_plugin_processor,
                          'faust': engine.make_faust_processor,
                          'add': engine.make_add_processor}
        self.tracks = [Track(track_data, self.functions)
                       for track_data in self.style_data.tracks]

    def test_create_final_proc_channel_bad(self):
        for track in self.tracks:
            del track.proc_funcs['faust']
            print(track.proc_funcs)
            with self.assertRaises(FaustProcessorNotFound):
                track.create_final_proc_channel('test_name')
            break

    def test_create_final_proc_channel_ok(self):
        for i, track in enumerate(self.tracks):
            proc = track.create_final_proc_channel(track.track_name)
            self.assertTrue(proc)
            self.assertEqual(proc.get_name(), track.track_name)
            self.assertTrue(proc.compiled)

    def test_create_final_proc_channel_bad2(self):
        for i, track in enumerate(self.tracks):
            proc = track.create_final_proc_channel('wrong_name')
            self.assertNotEqual(proc.get_name(), track.track_name)



class TestSuite3(unittest.TestCase):
    def setUp(self):
        parser = ConfigParser()
        self.style_data = parser.build_style_data(cfg.STYLE)

        engine = RenderEngine(cfg.SAMPLE_RATE, cfg.BUFFER_SIZE)
        self.functions = {'vst': engine.make_plugin_processor,
                          'faust': engine.make_faust_processor,
                          'add': engine.make_add_processor}
        self.tracks = [Track(track_data, self.functions)
                       for track_data in self.style_data.tracks]
        for track in self.tracks:
            track.construct()

    def test_get_track_tuples(self):
        for track in self.tracks:
            tuples, out_name = track.get_track_tuples()
            self.assertIsInstance(tuples, list)
            self.assertIsInstance(out_name, str)

            for processor, input in tuples:
                self.assertIsInstance(processor, (PluginProcessor, AddProcessor,
                                                  FaustProcessor))
                self.assertIsInstance(input, list)