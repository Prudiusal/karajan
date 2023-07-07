from pathlib import Path
import shutil
from uuid import uuid4

from Exceptions import WrongJsonFormatError, CSVNotFoundError, MidiNotFoundError, \
    BPMNotFoundError
from itertools import groupby

from logger import logger_conf
from mido import MidiFile, bpm2tempo, tempo2bpm, MetaMessage
from colors import red
import csv

# import settings as cfg


class SongConfig:
    """
        Class for the Song Configuration (just for one being used).
    """
    def __init__(self, d):
        self.Tracks = None
        self.Artist = None
        self.Name = None
        self.BPM = None
        self.OutputPath = None
        self.song_length = None
        self.rendered_output_path = None
        if not isinstance(d, dict):
            raise WrongJsonFormatError
        self.__dict__ = d

    def load_csv(self, csv_path):
        if not Path(csv_path).is_file():
            raise CSVNotFoundError
        with open(csv_path, 'r' ) as f:
            file = csv.reader(f)
            for artist, song, bpm in file:
                song = ' '.join(song.split(' ')).lower()

                if song in self.Name.lower():
                    logger_conf.info(f'BPM is set to {bpm}')
                    self.BPM = int(bpm)
                    return

        logger_conf.error(f'BPM NOT FOUND IN CSV for {self.Name}')
        return

    def prepare(self):
        self.duplicate_midi_tmp()
        if not hasattr(self, 'BPM'):
            self.BPM = self.get_bpm_from_msgs()
            # logger_render.warning(red(str(song_data.get_bpm_from_msgs())))
        self.delete_tempo_msgs()
        self.song_length = self.calculate_length()
        Path(self.OutputPath).mkdir(exist_ok=True, parents=True)
        self.rendered_output_path = self.OutputPath + f'{self.Name}' + '.wav'
        return True

    def calculate_length(self):
        if not hasattr(self, 'BPM') or not self.BPM:
            raise BPMNotFoundError
        logger_conf.warning(red(f'Bmp {self.BPM} is used'))
        times = []
        for track in self.Tracks:
            # path = track.get('tmp_midi_path', track.get('midi_path'))
            path = track['tmp_midi_path']
            try:
                mid = MidiFile(str(path))
            except Exception as e:
                logger_conf.error(e)
                continue
            times.append(mid.length)
        length = max(times) + 1
        k = 120 / self.BPM  # default tempo corresponds to bpm=120
        return int(k * length)

    def delete_tempo_msgs(self):
        flag = False
        for song_track in self.Tracks:
            midi_file = song_track['tmp_midi_path']
            # TODO: look for the mido exceptions
            mid = MidiFile(midi_file)
            for i, track in enumerate(mid.tracks):
                track_filtered = [msg for msg in track
                                  if msg.type != 'set_tempo']
                if len(track_filtered) != len(track):
                    flag = True
                mid.tracks[i] = track_filtered
            mid.save(midi_file)
        return flag

    def get_bpm_from_msgs(self):
        for song_track in self.Tracks:
            midi_file = song_track['tmp_midi_path']
            mid = MidiFile(midi_file)
            bpms = []
            for i, track in enumerate(mid.tracks):
                bpms.extend([int(tempo2bpm(msg.tempo)) for msg in track
                             if msg.type == 'set_tempo'])
                # ms = [msg.type for msg in track
                #       if msg.type not in ['note_on', 'note_off']]
                # # print(red(str(bpms)))
                # # print(red(str(ms)))
            if not len(bpms):
                logger_conf.error('Tempo messages not found!')
                return 120
            elif len(bpms) == 1 or len(set(bpms)) == 1:
                logger_conf.info(f'Tempo {bpms[0]} found')
                return bpms[0]
            else:
                logger_conf.error(f'FOUND {len(set(bpms))} : {set(bpms)}')
                logger_conf.error(f'{bpms[0]} is used')
                return bpms[0]

    def duplicate_midi_tmp(self):
        """
        Creates copy of the song in ./tmp folder
        This allows to change the midi files while
        the processing, without changing the original file
        """
        self.tmp_path = Path('.') / 'tmp' / 'midi'
        print(self.tmp_path.absolute())
        self.tmp_path.mkdir(parents=True, exist_ok=True)
        # self.tmp_path = Path(cfg.TMP_MIDI_PATH)
        for track in self.Tracks:
            new_name = str(uuid4()) + '.mid'
            tmp_midi_path = self.tmp_path / new_name
            if not Path(track['midi_path']).exists():
                raise MidiNotFoundError
            shutil.copy(track['midi_path'], tmp_midi_path.absolute())
            logger_conf.debug(f'{track["midi_path"]} copied into '
                              f'{str(self.tmp_path)} as '
                              f'{new_name}')
            track['tmp_midi_path'] = tmp_midi_path.absolute()

    def set_length_attribute(self):
        """NOT USED"""
        times = []
        for track in self.Tracks:
            path = track.get('tmp_midi_path', track.get('midi_path'))
            try:
                mid = MidiFile(str(path))
            except Exception as e:
                logger_conf.error(e)
                logger_conf.info('length of 100 seconds is used')
                times.append(100)
                continue
            times.append(mid.length)
        self.Length = min(times)
        return True

    # Next methods are not used currently
    def set_or_validate_bpm(self, bpm):
        """
        NOT USED
        Logic: if the bpm is presented in a style configuration, there should x
        be a self.bpm with a value (None in other case).

        To change the bpm midi file should be changed, so there is a need to
        save a copy of a midi file without changing the initial one.

        To add simplicity and provide the same workflow for all the cases, all
        midi file will be duplicated in a ./tmp folder of a project (with the
        same relative path.
        """
        if not bpm:
            return False
            self.get_bpm()
            logger_conf.info(f'Initial bpm is {self.bpm}')
            return True
        else:
            return False
            self.change_bpm(bpm)
            logger_conf.info(f'Changed bpm is {self.bpm}')
            return True

    def change_bpm(self, bpm):
        """NOT USED"""
        logger_conf.debug(f'bpm is changing to {bpm}')
        for track in self.Tracks:
            midi_file_path = track['tmp_midi_path']
            self.change_bpm_midifile(midi_file_path, bpm)
            # TODO: probably unchanged midi track shold be removed
        self.bpm = bpm
        return True

    def change_bpm_midifile(self, filename, bpm):
        """NOT USED"""
        try:
            mid = MidiFile(filename)
        except Exception as e:
            logger_conf.error(e)
        tempo = bpm2tempo(bpm)
        if not self.change_tempo(mid, tempo):  # 'Tempo haven\'t changed'
            self.add_set_tempo_msg(mid, bpm)
        mid.save(filename)
        return True

    @staticmethod
    def add_set_tempo_msg(mid, bpm):
        """NOT USED"""
        set_tempo_msg = MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0)
        mid.tracks[0].append(set_tempo_msg)

    @staticmethod
    def change_tempo(mid, new_tempo):
        """NOT USED"""
        flag: bool = False
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    msg.tempo = new_tempo
                    flag = True
        return flag

    def get_bpm(self):
        """NOT USED"""
        logger_conf.debug('Getting the bpm')
        bpms = []
        for track in self.Tracks:
            midi_file_path = track['tmp_midi_path']
            bpm = self.get_bpm_midifile(midi_file_path)
            if bpm:
                bpms.append(bpm)
                # TODO: probably unchanged midi track shold be removed
        if not bpms:
            logger_conf.debug('No bpm found for the mid')
            logger_conf.debug('Default bpm 120 is used')
            self.bpm = 120
            return True
        elif all_equal(bpms):
            self.bpm = bpm
            return True

    @staticmethod
    def get_bpm_midifile(filename):
        """NOT USED"""
        try:
            mid = MidiFile(filename)
        except Exception as e:
            logger_conf.error(e)
        tempos = []
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempos.append(msg.tempo)
        if not tempos:
            return 120
        elif all_equal(tempos):
            return tempo2bpm(tempos[0])
        elif not all_equal(tempos):
            # TODO: if has not changed -> create message or delete midi
            # self.change_tempo(mid, tempo2bpm(tempos[0]))
            mid.save(filename)
            return tempo2bpm(tempos[0])


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

