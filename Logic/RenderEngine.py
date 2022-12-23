import time
from os.path import isfile

from scipy.io import wavfile
import dawdreamer

from logger import logger_render
from track import Track


class RenderEngine(dawdreamer.RenderEngine):
    def __init__(self, sample_rate=44100, buffer_size=128):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        super().__init__(self.sample_rate, self.buffer_size)
        self.tracks = {}
        self.graph = []

    # :TODO Override ___init___(), if you need a custom values for the buffer
    # :size
    # :REPORT We can set it while creation, or I didn't get the idea

    def create_tracks(self, style):
        for track_data in style.tracks:
            print()
            print()
            func = self.make_plugin_processor
            track_name = track_data['track_name']
            self.tracks[track_name] = Track(track_data)
            self.tracks[track_name].construct(func)
            # self.tracks.append(track)
            # setattr(self, track_data['track_name'],
            #         track.construct(func))
            print()

    def construct_graph(self):
        adder_args = []
        for track in self.tracks.values():
            print()
            print()
            track_tuples, track_output = track.get_track_tuples()

            self.graph.extend(track_tuples)
            adder_args.append(track_output)
        add_processor = self.make_add_processor('add_processor',
                                                [1]*len(adder_args))
        self.graph.append((add_processor, adder_args))
        print()
        logger_render.info(self.graph)
        print()

    def process_song(self, song_data):
        logger_render.debug('\nSong processing has started:')
        BPM = song_data.BPM
        logger_render.debug(BPM)
        song_length = song_data.SongLengthInSeconds
        logger_render.debug(song_length)
        output_path = song_data.OutputPath
        logger_render.debug(output_path)

        self.load_midi_into_tracks(song_data.Tracks)
        logger_render.info('\nMidi files are loaded\n')

        self.load_graph(self.graph)

        logger_render.debug('Started Rendering.')
        self.render(song_data.SongLengthInSeconds)
        logger_render.debug('Finished Rendering.')
        audio = self.get_audio()
        logger_render.debug(f'{audio}')
        logger_render.debug(f'{type(audio)}')

        rendered_output_path = song_data.OutputPath + \
            f'demo_{int(time.time())}.wav'
        logger_render.info(f'output path is {rendered_output_path}')
        wavfile.write(rendered_output_path, self.sample_rate,
                      audio.transpose())
        if isfile(rendered_output_path) is not None:
            logger_render.warning('Problem with output path')

    def load_midi_into_tracks(self, tracks_data):
        for ch in tracks_data:
            ch_name = ch['track_name']
            midi_path = ch['midi_path']
            logger_render.debug(f'midi_path {midi_path}')
            self.tracks[ch_name].plugins[0].plugin.load_midi(midi_path)

    def preconfigure_renderer(self):
        self.engine(self.sample_rate, self.buffer_size)
        self.engine.set_bpm(120.)

    def build_graph(self, serum_processor):
        logger_render.debug('Building graph ...')
        graph = []
        graph.append((serum_processor, []))
        self.load_graph(graph)

    def render_to_file(self, song_data, sample_rate=44100):
        logger_render.debug('Started Rendering.')
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
