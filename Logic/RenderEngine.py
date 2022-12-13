import time
from os.path import isfile

from scipy.io import wavfile
import dawdreamer


class RenderEngine(dawdreamer.RenderEngine):
    # :TODO Override ___init___(), if you need a custom values for the buffer size
    def preconfigure_renderer(self):
        self.engine(self.sample_rate, self.buffer_size)
        self.engine.set_bpm(120.)

    def build_graph(self, serum_processor):
        print("Building graph...")
        graph = []
        graph.append((serum_processor, []))
        self.load_graph(graph)

    def render_to_file(self, song_data, sample_rate=44100):
        print("Started Rendering.")
        self.render(song_data.length)
        audio = self.get_audio()
        # :TODO Add a "if-silent" check (Check if audio has some sound in it)
        # if audio.mean() != 0.0:
        #     raise SynthesisError('Synthetized audio is silent. Check VSTi parameters')

        rendered_output_path = song_data.output_path + f'demo_{int(time.time())}.wav'
        wavfile.write(rendered_output_path, sample_rate, audio.transpose())
        if isfile(rendered_output_path) is not None:
            print(f"Successfully finished rendering:\n{rendered_output_path}")
