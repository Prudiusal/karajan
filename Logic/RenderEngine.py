import datetime
from os.path import isfile

from scipy.io import wavfile
import dawdreamer

from logger import logger_render
from track import Track
# from pm_tests import get_mid_length


class RenderEngine(dawdreamer.RenderEngine):
    """
    Main class of the project, it implements the functionality
    of a DAW. Configuration is set by 'style_config', which 
    is created in a ConfigParser.py

    Configured object of this class can render multiple midi 
    tracks as one song. For each track midi file is loaded. 

    Additional configuration of the BPM is allowed through 
    the setting in 'song_data'.

    Creates engine, stores tracks configuration for the style.
    """
    def __init__(self, sample_rate=44100, buffer_size=128):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        super().__init__(self.sample_rate, self.buffer_size)
        self.tracks = {}
        self.graph = []
        self.style_name = None
        self.bpm = None
        self.bpm_from_song = None
        self.rendered_output_path = None

    def create_tracks(self, style):
        """
        Creates the instances for each track of the song.
        :param style: StyleConf object, contains the information of
        each tracks in a style. For each track the plugins and presets
        are noticed.
        """
        self.style_name = style.name
        # self.bpm = getattr(style, 'bpm', None)
        # here we save and pass the functions to create a processors with
        # this engine.
        functions = {'vst': self.make_plugin_processor,
                     'faust': self.make_faust_processor,
                     'add': self.make_add_processor}

        for track_data in style.tracks:
            track_name = track_data['track_name']
            self.tracks[track_name] = Track(track_data, functions)
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
                                                [1] * len(adder_args))
        self.graph.append((add_processor, adder_args))
        logger_render.debug(self.graph)

    def process_song(self, song_data):
        """
        Loads midi files, renders, saves.
        :param song_data: SongConfig instance with all data for the song.
        """
        logger_render.info(f'{song_data.Name} processing has started:')
        song_data.duplicate_midi_tmp()
        # TODO: save initial bpm (from set_tempo msgs)
        song_data.delete_tempo_msgs()
        song_length = song_data.calculate_length()

        self.load_midi_into_tracks(song_data)
        logger_render.debug('Midi files are loaded\n')
        self.set_bpm(song_data.BPM)
        self.load_graph(self.graph)
        logger_render.info(f'Started Rendering - {song_length}')
        time_rendering_start = datetime.datetime.now()
        self.render(song_length)
        time_rendering = datetime.datetime.now() - time_rendering_start
        logger_render.info('Finished Rendering, time:'
                           f'{time_rendering.seconds}')
        self.rendered_output_path = song_data.OutputPath + \
            f'{datetime.datetime.now().strftime("%m-%d_%H-%M-%S")}_' + \
            f'{song_data.Artist}' + \
            f'{song_data.Name}_{self.style_name}.wav'

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
        # midi_times = []
        for params in song_data.Tracks:
            track_name = params['track_name']
            midi_path = params['tmp_midi_path']
            processors = self.tracks[track_name].processors
            synth = next(iter(processors.values()))  # take 1st
            if midi_path.exists():
                try:
                    synth.load_midi(str(midi_path), beats=True)
                except Exception as e:
                    logger_render.error(f'Exception {e} occured')
            else:
                logger_render.error(f'midi file not found {midi_path}')
        # logger_render.debug(midi_times)
        # self.length_from_midi = song_data.Length
        # self.bpm_from_song = song_data.__dict__.get('BPM', None)
