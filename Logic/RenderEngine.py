import time
from os.path import isfile

from scipy.io import wavfile
import dawdreamer

from logger import logger_render


class RenderEngine(dawdreamer.RenderEngine):
    # :TODO Override ___init___(), if you need a custom values for the buffer
    # :size
    # :REPORT We can set it while creation, or I didn't get the idea

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
