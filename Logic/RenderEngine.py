import datetime
import os
import platform
from os.path import isfile
from pathlib import Path

import dawdreamer
import librosa
import numpy as np

# from scipy.io import wavfile
import soundfile as sf
from Exceptions import BPMNotFoundError, TracksNotFoundError, WrongStyleType
from logger import logger_render

if platform.system() == "Darwin":
    from pydub import AudioSegment

from style_config import StyleConfig
from track import Track

import settings as cfg

# from colors import red


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
        self.song_length = None
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        super().__init__(self.sample_rate, self.buffer_size)
        self.tracks = {}
        self.master = None  # Track instance
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
        if not isinstance(style, StyleConfig):
            raise WrongStyleType(
                f" instead of {type(style)} should be " "StyleConfig"
            )

        self.style_name = style.name
        # self.bpm = getattr(style, 'bpm', None)
        # here we save and pass the functions to create a processors with
        # this engine.
        functions = {
            "vst": self.make_plugin_processor,
            "faust": self.make_faust_processor,
            "add": self.make_add_processor,
            "pb": self.make_playback_processor,
            "pbw": self.make_playbackwarp_processor,
        }

        for track_data in style.tracks:
            track_name = track_data["track_name"]
            self.tracks[track_name] = Track(track_data, functions)
            self.tracks[track_name].construct()  # creates all vst plugins

        if hasattr(style, "master"):
            self.master = Track(style.master, functions)
            self.master.construct()

    def construct_graph(self):
        """
        Asks each track of the song to create the tuples for the graph.
        Then combines them in a list.
        Graph is created in accordance with DawDreamer rules.
        """
        adder_args = []
        if not self.tracks:
            raise TracksNotFoundError
        for track in self.tracks.values():
            track_tuples, track_output = track.get_track_tuples()  # no init
            self.graph.extend(track_tuples)  # tuples of processors
            adder_args.append(track_output)  # we are adding the last to adder

        logger_render.debug(f"{len(adder_args)} input channels for Adder")
        adder_name = "add_proc"
        add_processor = self.make_add_processor(
            adder_name, [1] * len(adder_args)
        )
        self.graph.append((add_processor, adder_args))

        if self.master:
            tuples, output = self.master.get_track_tuples(adder_name)
            self.graph.extend(tuples)  # tuples of processors

        logger_render.debug(self.graph)

    def process_song(self, song_data):
        """
        renders, saves.
        :param song_data: SongConfig instance with all data for the song.
        """
        logger_render.info(f"{song_data.Name} processing has started:")

        # false + false
        if not (hasattr(song_data, "BPM") or song_data.check_if_playback()):
            raise BPMNotFoundError
        else:  # we have not pure midi config, but still there is a BPM in conf
            if song_data.BPM:
                self.set_bpm(song_data.BPM)

        logger_render.debug("Trying to load the midi")
        self.load_data_into_tracks(song_data)
        logger_render.debug("midis are loaded")

        self.song_length = song_data.song_length
        if not self.song_length > 0:
            logger_render.error(f"The length is {self.song_length}")

        logger_render.debug("Midi and MP3 files are loaded")
        self.load_graph(self.graph)
        logger_render.info(f"Started Rendering - {song_data.song_length}")
        time_rendering_start = datetime.datetime.now()
        self.render(song_data.song_length)
        time_rendering = datetime.datetime.now() - time_rendering_start
        logger_render.info(
            "Finished Rendering, time:" f"{time_rendering.seconds}"
        )

    def process_wav(self, song_data):
        """
        The function "process_wav" processes a WAV file by loading it into
        tracks, loading a graph, and rendering the file.

        :param song_data: The `song_data` parameter is an object that
        contains information about a song.
        """
        print("shouldn't be here (process_wav)")
        logger_render.info(f"{song_data.Name} processing has started:")
        # convert to load wav into tracks
        self.load_midi_into_tracks(song_data)

        self.song_length = song_data.song_length
        logger_render.debug("Midi files are loaded\n")

        self.load_graph(self.graph)
        logger_render.info(f"Started Rendering - {song_data.song_length}")
        time_rendering_start = datetime.datetime.now()
        self.render(song_data.song_length)
        time_rendering = datetime.datetime.now() - time_rendering_start
        logger_render.info(
            "Finished Rendering, time:" f"{time_rendering.seconds}"
        )

    def save_audio(self, rendered_output_path):
        """
        Saves audio file ( now in a ./WAVs folder)
        """
        audio = self.get_audio()
        transposed = audio.transpose()

        logger_render.info(f"output path is {rendered_output_path}")
        sf.write(
            rendered_output_path,
            transposed,
            samplerate=44100,
            subtype="PCM_16",
        )
        if not isfile(rendered_output_path):
            logger_render.error("File is not saved")

        if platform.system() == "Darwin":
            path_wav = str(rendered_output_path.absolute())
            path_mp3 = path_wav.split(".")[0] + ".mp3"
            AudioSegment.from_wav(path_wav).export(
                path_mp3, format="mp3", bitrate="256k"
            )
            os.remove(rendered_output_path)

        # path_mp3 = '.'.join(rendered_output_path.split('.')[:-1]) + '.mp3'
        # # with af.AudioFile(self.rendered_output_path) as f:
        # #     audio_data = f.read()
        # # with af.AudioFile(path_mp3, 'w', af.Format('mp3', 'pcm')) as f:
        # #     f.write(audio_data)
        # # wav_file = AudioSegment.from_wav(rendered_output_path)
        # # wav_file.export(path_mp3, format='mp3')
        # # os.remove(rendered_output_path)
        #
        # if not isfile(path_mp3):
        #     logger_render.error('File is not saved')

    def load_data_into_tracks(self, song_data):
        """
        Loads the midi and mp3 files from the config to the appropriate synths.
        """
        # midi_times = []
        self.clear_pb_data()
        for params in song_data.Tracks:
            track_name = params["track_name"]
            try:
                processors = self.tracks[track_name].processors
            except KeyError:
                logger_render.error(f"Track {track_name} is not found")  # for
                # f'the midi {midi_path} ({params["midi_path"]}')
                continue
            # take 1st plug in of the track
            player = next(iter(processors.values()))

            midi_path = params.get("tmp_midi_path")
            mp3_path = params.get("mp3_path")
            if midi_path and Path(midi_path).exists():
                try:
                    player.load_midi(midi_path, beats=True)
                except Exception as e:
                    logger_render.error(
                        f"Exception {e} occurred during the "
                        f"load of the midi {midi_path} "
                        f"into the track {track_name}"
                    )
                else:
                    logger_render.debug(
                        f"{midi_path} is loaded into {track_name}"
                    )

            elif mp3_path and Path(mp3_path).exists():
                try:
                    data = self.get_audio_data(mp3_path)
                    player.set_data(data)
                except Exception as e:
                    logger_render.error(
                        f"Exception {e} occurred during the "
                        f"load of the MP3 {mp3_path} "
                        f"into the track {track_name}"
                    )
                else:
                    logger_render.debug(
                        f"{mp3_path} is loaded into " f"{track_name}"
                    )
            else:
                logger_render.error(f"midi file not found {midi_path}")

    def clear_pb_data(self):
        """
        The function clears the data of playback processors in a DawDreamer
        object.
        """
        for track in self.tracks.values():
            processor = next(iter(track.processors.values()))
            if isinstance(processor, dawdreamer.dawdreamer.PlaybackProcessor):
                empty_data = np.zeros([2, 1], dtype="float32")
                processor.set_data(empty_data)

    @staticmethod
    def get_audio_data(mp3_path):
        sig, rate = librosa.load(mp3_path, mono=False, sr=cfg.SAMPLE_RATE)
        return sig
