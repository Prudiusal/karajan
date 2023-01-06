import time
import datetime
from os.path import isfile

from scipy.io import wavfile
import dawdreamer

from logger import logger_render
from track import Track
from pm_tests import get_mid_length


class RenderEngine(dawdreamer.RenderEngine):
    """
    Creates engine, stores tracks configuration for the style.
    """
    def __init__(self, sample_rate=44100, buffer_size=128):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        super().__init__(self.sample_rate, self.buffer_size)
        self.tracks = {}
        self.graph = []

    def create_tracks(self, style):
        """
        Creates the instances for each track of the song.
        :param style: StyleConf object, contains the information of
        each tracks in a style. For each track the plugins and presets
        are noticed.
        """
        self.style_name = style.name
        self.bpm = int(style.bpm)
        self.set_bpm(300.)  # TODO add test to check being unchanged
        for track_data in style.tracks:
            track_name = track_data['track_name']
            self.tracks[track_name] = Track(track_data,
                                            self.make_plugin_processor,
                                            self.make_add_processor)
            self.tracks[track_name].construct()  # creates all vst plugins

    def construct_graph(self):
        """
        Asks each track of the song to create the tuples for the graph.
        Then combines them in a list.
        Graph is created in accordance with DawDreamer rules.
        """
        adder_args = []
        for track in self.tracks.values():
            track_tuples, track_output = track.get_track_tuples()
            self.graph.extend(track_tuples)
            adder_args.append(track_output)
        logger_render.debug(f'{len(adder_args)} input channels for Adder')
        add_processor = self.make_add_processor('add_processor',
                                                [1]*len(adder_args))
        self.graph.append((add_processor, adder_args))
        logger_render.debug(self.graph)

    def process_song(self, song_data):
        """
        Loads midi files, renders, saves.
        :param song_data: SongConfig instance with all data for the song.
        """
        logger_render.info(f'{song_data.Name} processing has started:')
        self.load_midi_into_tracks(song_data)
        logger_render.debug('Midi files are loaded\n')
        self.load_graph(self.graph)
        # assert self.bpm == self.get_bpm(), "The bpm has changed"
        logger_render.info(f'Started Rendering - {self.length_from_midi}.')
        self.render(self.length_from_midi)
        self.rendered_output_path = song_data.OutputPath + \
            f'{datetime.datetime.now().strftime("%m-%d_%H-%M-%S")}_' + \
            f'{song_data.Name}_{self.style_name}.wav'
        logger_render.debug('Finished Rendering.')
        self.save_audio()

    def save_audio(self):
        """
        Saves audio file ( now in a ./WAVs folder)
        """
        audio = self.get_audio()
        logger_render.info(f'output path is {self.rendered_output_path}')
        wavfile.write(self.rendered_output_path, self.sample_rate,
                      audio.transpose())
        if not isfile(self.rendered_output_path):
            logger_render.error('File is not saved')

    def load_midi_into_tracks(self, song_data):
        """
        Loads the midi files from the config to the appropriate synths.
        """
        midi_times = []
        for params in song_data.Tracks:
            track_name = params['track_name']
            midi_path = params['midi_path']
            processors = self.tracks[track_name].processors
            synth = next(iter(processors.values()))  # take 1st
            if isfile(midi_path):
                synth.load_midi(midi_path, beats=False)
                midi_times.append(get_mid_length(midi_path, song_data.BPM, self.bpm))
            else:
                logger_render.warning(f'midi file not found {midi_path}')

        self.length_from_midi = max(midi_times)

    # def preconfigure_renderer(self):
    #     """Not used right now"""
    #     self.engine(self.sample_rate, self.buffer_size)
    #     self.engine.set_bpm(120.)

    def build_graph(self, serum_processor):
        """Not used right now"""
        logger_render.debug('Building graph ...')
        graph = []
        graph.append((serum_processor, []))
        self.load_graph(graph)

    def render_to_file(self, song_data, sample_rate=44100):
        """Not used right now"""
        logger_render.info('Started Rendering.')
        self.render(song_data.length)
        audio = self.get_audio()
        # :TODO Add a "if-silent" check (Check if audio has some sound in it)
        # if audio.mean() != 0.0:
        #     raise SynthesisError('Synthetized audio is silent. Check VSTi'
        # 'parameters')

#   def load_plugin(MidiVST):
#       plug = self.plugin_processor(MidiVST.name, plugin_conf.path)
#        plug.load_preset(plugin_conf.preset)
#       if plugin_conf.midi:
#           plug.load_midi(plugin_conf_midi)

        rendered_output_path = song_data.output_path + \
            f'demo_{int(time.time())}.wav'
        logger_render.debug(f'output path is {rendered_output_path}')
        wavfile.write(rendered_output_path, sample_rate, audio.transpose())
        if isfile(rendered_output_path) is not None:
            logger_render.info(
                f'Successfully rendered:\n{rendered_output_path}')
