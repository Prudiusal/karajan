import json
import math
from pathlib import Path
from logger import logger_sel


class Selector:
    names_to_delete = ['Bell', 'Castanets', 'Timpani', 'Maracas', 'clap',
                       'Timpani', 'Harp', 'FX', 'Xylophone', 'horn', 'Flutes',
                       'Vibraphone', 'Bongos', 'Shaker', 'Cymbal', ]

    def select_tracks(self, song_config):
        pass

    def __call__(self, config):
        # orig = len(config.get('Tracks'))
        logger_sel.debug(f'{config.get("Name")} - Config is in processing')

        config = self.add_times(config)
        config, _ = self.clear_empty(config)
        # empt = len(config.get('Tracks'))

        num_tracks_to_remove = math.floor(len(config['Tracks']) * 0.3)
        # order = self.tracks_time_ordered(config)
        # logger_sel.debug('INIT: \n'
        #                  f'{list(zip(*self.tracks_time_ordered(config)))[0]}')
        logger_sel.debug('INIT: \n'
                         f'{self.tracks_time_ordered(config)}')
        logger_sel.debug(f'{num_tracks_to_remove=}')
        # config['original_tracks'] = len(config['Tracks'])
        config, num_cleared = self.clear_names(config)
        # names = len(config.get('Tracks'))

        num_tracks_to_remove -= num_cleared
        order = self.tracks_time_ordered(config)
        config, _ = self.remove_shortest(config, order, num_tracks_to_remove)
        # final = len(config.get('Tracks'))

        # logger_sel.debug('FINAL: \n'
        #                  f'{list(zip(*self.tracks_time_ordered(config)))[0]}')
        logger_sel.debug('FINAL: \n'
                         f'{self.tracks_time_ordered(config)}')

        # print(f'{final=}, {names=}, {empt=}, {orig=}')
        # input()
        return config

    def clear_empty(self, config):
        orig = len(config.get('Tracks'))
        tracks = [t for t in config['Tracks'] if t['total_time'] > 1]
        config['Tracks'] = tracks
        final = len(config.get('Tracks'))
        return config, orig - final

    def remove_shortest(self, config, order, num_to_remove):
        orig = len(config.get('Tracks'))
        if num_to_remove < 1:
            return config, 0

        tracks_to_remove = order[:num_to_remove]
        logger_sel.debug(f'{tracks_to_remove=}')
        tracks = [t for t in config['Tracks'] if t['stem_name'] not in
                  list(zip(*tracks_to_remove))[0]]
        config['Tracks'] = tracks
        final = len(config.get('Tracks'))
        return config, orig - final

    def clear_names(self, config):
        orig = len(config.get('Tracks'))
        ids_remove = []
        for i, track in enumerate(config.get('Tracks')):
            if any([inst.lower() in track.get('stem_name').lower() for inst in
                    self.names_to_delete]):
                ids_remove.append(i)
        for i in sorted(ids_remove, reverse=True):
            config.get('Tracks').pop(i)
        final = len(config.get('Tracks'))
        return config, orig - final

    def add_times(self, config):
        name = config.get('Name')
        for track in config.get('Tracks'):
            if not Path(track.get('steps_path')).exists():
                logger_sel.error(f'{name} - no Steps json')
                continue
            with open(track.get('steps_path'), 'r') as js:
                time = 0
                data = json.load(js)
                if not isinstance(data, list):
                    logger_sel.error(f'{name} - Json in wrong format')
                    continue
                track['steps'] = data
                for interval in data:
                    try:
                        time += interval['endTime'] - interval['startTime']
                    except KeyError:
                        logger_sel.error(f'{name} - Keys not found for the '
                                         'interval')
                        continue
                track['total_time'] = round(time, 1)
        return config

    def tracks_time_ordered(self, config):
        times = [(track.get('stem_name'), track.get('total_time')) for track in
                 config.get('Tracks')]
        times.sort(key=lambda x: x[1], reverse=False)
        return times
