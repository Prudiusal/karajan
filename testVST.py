import os
from pathlib import Path
from scipy.io import wavfile
import dawdreamer as daw
from setup import check_and_update_plugin_paths

class MyEngine(daw.RenderEngine):

    def create_structure_from_dirs(self, folder: Path, ) -> list:
        """
        Creates the structure of the track by the folders and presets. Loads required plugins into the engine.
        """
        path = folder.resolve()
        graph, adder_args = [], []
        name = 'NOT_LOADED'
        for track in [pth for pth in path.iterdir() if pth.is_dir()]:
            previous = ''
            plugin, midi_player_plugin = '', ''
            for file in sorted([pth for pth in track.iterdir() if pth.is_file()]):
                if 'mid' in file.name:  # if its a midi file -> load it into the synth plugin
                    getattr(self, midi_player_plugin).load_midi(str(file), beats=True)
                    continue
                position, plugin = file.name.split('.')[0].split('_')  # the name of preset contains it
                name = plugin + '_' + track.name
                path_to_plugin = os.environ.get(plugin.upper())
                setattr(self, name, self.make_plugin_processor(name, path_to_plugin))  # create the processor
                # if file.name.endswith('vst3'):
                #     getattr(self, name).load_vst3_preset(str(file))
                #     getattr(self, name).open_editor()
                getattr(self, name).load_preset(str(file))  # load preset into previously created plugin processor
                if int(position) is 0:  # we suppose, that synth is on the 0-th position of the folder
                    midi_player_plugin = name  # if the midi file will be found, is will be loaded into this processor
                    graph.append((getattr(self, name), []))  # add the new track into the graph
                else:
                    graph.append((getattr(self, name), [previous]))  # we add new processor to a graph, the source of
                    # sound is in the squared brackets
                previous = name  # save the name of the last-used plugin, to use it the chain
            adder_args.append(getattr(self, name).get_name())  # the summed up audio is obtained by the add processor,
            # so for each track we should be aware of the last one
        graph.append(tuple([self.make_add_processor('add', [.7]*len(adder_args)), adder_args]))  # all plugins are ready
        return graph


def main():
    """
    Creates the track from the files of folder in variable 'directory' with help of DawDreamer and saves the results
    into this folder.
    """
    # Parameters of the engine
    sample_rate = 44100
    buffer_size = 128
    plugin_environment_variables = ['SERUM', 'VALHALLAFREQ', 'VALHALLASUPER', ]
    check_and_update_plugin_paths(plugin_environment_variables)
    directory = Path('demo')  # the path to the track files
    # https://dirt.design/DawDreamer/
    engine = MyEngine(sample_rate, buffer_size)  # create dawdreamer engine
    graph = engine.create_structure_from_dirs(directory, )
    engine.load_graph(graph)
    engine.render(100)
    audio = engine.get_audio()
    save_path = directory / 'demo1.wav'
    wavfile.write(save_path, sample_rate, audio.transpose())


if __name__ == '__main__':
    main()
