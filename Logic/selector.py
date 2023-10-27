import json
import math
from pathlib import Path

from Exceptions import (
    StemsDeletionError,
    StemsNotDeletedError,
    UnableToDeleteStemsError,
)
from logger import logger_sel

# from typing import List, Dict


class Selector:
    k_remove = 0.3
    silence_max_time = 1.5
    names_to_delete = [
        "Bell",
        "Castanets",
        "Timpani",
        "Maracas",
        "clap",
        "Timpani",
        "Harp",
        "FX",
        "Xylophone",
        "horn",
        "Flutes",
        "Vibraphone",
        "Bongos",
        "Shaker",
        "Cymbal",
    ]

    def __call__(self, config):
        """
        The above function takes a configuration as input, processes it by
        removing certain tracks based on specified criteria, and returns the
        modified configuration.

        :param config: The `config` parameter is a dictionary that contains
        various configuration settings for processing audio tracks. It
        likely includes information such as the name of the track,
        the artist, and a list of tracks to be processed :return: the
        modified `config` dictionary.
        """
        # we have to check if the stem is 'crutial', it means it solely plays
        # plays during sume sufficeint period of time and its removal will
        # lead to silence in track
        logger_sel.info(f'{config.get("Name")} - Config is in processing')

        config = self.add_times(config)
        config, _ = self.clear_empty(config)
        original_number_of_tracks = len(config.get("Tracks"))

        if original_number_of_tracks == 1:
            raise StemsNotDeletedError(
                f'{config.get("Name")} -'
                f'{config["Artist"]} has only 1 not '
                f"empty stem"
            )

        num_tracks_to_remove = math.floor(
            len(config["Tracks"]) * self.k_remove
        )
        if num_tracks_to_remove == 0:
            num_tracks_to_remove = 1

        logger_sel.debug("INIT: \n" f"{self.tracks_time_ordered(config)}")
        logger_sel.debug(f"{num_tracks_to_remove=}")
        config, num_cleared_by_name = self.clear_names(config)

        num_tracks_to_remove -= num_cleared_by_name

        order = self.tracks_time_ordered(config)
        config, _ = self.remove_shortest(config, order, num_tracks_to_remove)
        logger_sel.debug("FINAL: \n" f"{self.tracks_time_ordered(config)}")

        if len(config.get("Tracks")) == 0:
            raise StemsDeletionError(
                f'{config.get("Name")} has 0 stems after ' "selection, Skipped"
            )

        final_number_of_tracks = len(config.get("Tracks"))
        if original_number_of_tracks == final_number_of_tracks:
            raise UnableToDeleteStemsError(
                f'{config.get("Name")} no deleted ' f"stems, Skipped"
            )
        return config

    @staticmethod
    def clear_empty(config):
        """
        The function `clear_empty` removes tracks from a configuration
        dictionary that have a total time less than or equal to 1 and
        returns the modified dictionary along with the number of tracks
        removed.

        :param config: The `config` parameter is a dictionary that contains
        information about tracks. It has a key "Tracks" which maps to a list
        of dictionaries. Each dictionary in the list represents a track and
        has keys such as "total_time" which represents the total time of the
        track :return: a tuple containing the modified "config" dictionary
        and the difference between the original number of tracks and the
        final number of tracks after removing those with a total time less
        than or equal to 1.
        """
        orig = len(config.get("Tracks"))
        tracks = [t for t in config["Tracks"] if t["total_time"] > 1]
        config["Tracks"] = tracks
        final = len(config.get("Tracks"))
        return config, orig - final

    def track_is_crutial(self, config, considering_index):
        """
        The function `track_is_crutial` determines if a track is crucial for
        a full song based on the amount of silence it contains.

        :param config: The `config` parameter is a dictionary that contains
        information about the tracks and steps in a song. It likely includes
        details such as the number of tracks, the steps in each track,
        and other relevant information :param considering_index: The
        `considering_index` parameter is the index of the track that is
        being considered for deletion. It is used to determine the steps of
        the track that will be added to the `periods` list :return: The
        method returns a boolean value. If the silence duration is less than
        the maximum allowed silence time, it returns False. Otherwise,
        it returns True.
        """
        # this method should be called each time before deletion of the channel
        # the remaining tracks should form the full song
        # if all the tracks are crutial -> exception should be raised
        periods = self.get_all_steps(config, considering_index)
        merged = self.merge_steps(periods)
        silence_without_idx = self.calculate_silence(merged)

        periods.extend(config["Tracks"][considering_index]["steps"])
        merged_with_idx = self.merge_steps(periods)
        silence_with_idx = self.calculate_silence(merged_with_idx)

        silence = silence_with_idx - silence_without_idx

        if silence < self.silence_max_time:
            return False
        else:
            return True

    # def merged_steps(periods: List[List[Dict{'startTime': int,
    # 'endTime': int}]]) -> List[Dict{'startTime': int, 'endTime': int}]:

    @staticmethod
    def get_all_steps(config, exclude_index):
        """
        The function `get_all_steps` returns a list of all steps from the
        tracks in a given configuration, excluding a specific track.

        :param config: The `config` parameter is a dictionary that contains
        information about tracks and steps. It has the following structure:
        :param exclude_index: The `exclude_index` parameter is an integer
        that specifies the index of the track that should be excluded from
        the result :return: a list of all the steps from the tracks in the
        given configuration, excluding the track at the specified index.
        """
        periods = []
        for i, track in enumerate(config["Tracks"]):
            if i == exclude_index:
                continue
            periods.extend(track["steps"])
        return periods

    @staticmethod
    def merge_steps(periods):
        """
        The function `merge_steps` takes a list of periods and merges
        overlapping or adjacent periods into a new list of combined periods.

        :param periods: The `periods` parameter is a list of dictionaries,
        where each dictionary represents a time period. Each dictionary has
        two keys: "startTime" and "endTime", which represent the start and
        end times of the period respectively :return: The function
        `merge_steps` returns a list of dictionaries representing combined
        time periods.
        """
        # result should be as a new period -> check empty time
        periods.sort(key=lambda x: x["startTime"])
        combined = [{"startTime": 0, "endTime": 0}]
        end_old = combined[0]["endTime"]

        for timeslot in periods:
            start_new = timeslot["startTime"]
            end_new = timeslot["endTime"]

            if start_new > end_old:
                combined.append(timeslot)
                end_old = end_new
            else:
                if end_new > end_old:
                    combined[-1][1] = end_new
                    end_old = end_new

        return combined

    @staticmethod
    def calculate_silence(timeslots):
        """
        The function calculates the total silence duration between
        consecutive timeslots.

        :param timeslots: The `timeslots` parameter is a list of
        dictionaries. Each dictionary represents a time slot and has two
        keys: "startTime" and "endTime". The value of "startTime" represents
        the start time of the time slot, and the value of "endTime"
        represents the end time of the time slot :return: the total silence
        duration in the given timeslots.
        """
        silence = 0
        init = 0
        for slot in timeslots:
            silence += slot["startTime"] - init
            init = slot["endTime"]
        return silence

    def remove_shortest(self, config, order, num_to_remove):
        """
        The function removes the shortest tracks from a given configuration
        based on a specified order and number to remove.

        :param config: The `config` parameter is a configuration object that
        contains information about the tracks and their properties. It is
        used to determine which tracks to remove :param order: The `order`
        parameter is a list of tuples, where each tuple contains the name of
        a track and its corresponding length :param num_to_remove: The
        parameter `num_to_remove` represents the number of tracks to remove
        :return: the result of the `clear_names` method called on `self`
        with the `config` and `tracks_to_remove_names` as arguments.
        """
        if num_to_remove < 1:
            return config, 0

        tracks_to_remove = order[:num_to_remove]
        tracks_to_remove_names = list(list(zip(*tracks_to_remove))[0])
        for i, name in enumerate(tracks_to_remove_names):
            if "drums" in name.lower():
                tracks_to_remove = order[: num_to_remove + 1]
                tracks_to_remove_names = list(list(zip(*tracks_to_remove))[0])

        logger_sel.debug(f"{tracks_to_remove=}")

        return self.clear_names(config, tracks_to_remove_names)

        # for i, track in enumerate(config['Tracks']):
        #     if track['stem_name'] in tracks_to_remove_names:
        #         ids_to_remove.append(i)

        # selected_tracks = []
        # for track in config['Tracks']:
        #     pass

        # tracks = [t for t in config['Tracks'] if t['stem_name'] not in
        #           track_to_remove_names and not]
        # config['Tracks'] = tracks
        # final = len(config.get('Tracks'))
        # return config, orig - final

    def clear_names(self, config, names_to_delete=None):
        """
        The function `clear_names` removes tracks from a configuration based
        on a list of names to delete, while protecting tracks with the word
        "drums" in their name.

        :param config: The `config` parameter is a dictionary that contains
        information about tracks. It has a key "Tracks" which maps to a list
        of dictionaries. Each dictionary in the list represents a track and
        contains information such as the track name, ID, and other
        properties :param names_to_delete: The `names_to_delete` parameter
        is a list of names that you want to delete from the `config` object.
        These names are case-insensitive and will be compared with the
        `stem_name` attribute of each track in the `config` object. If a
        track's `stem_name` contains :return: a tuple containing the
        modified `config` dictionary and the difference between the original
        number of tracks and the final number of tracks.
        """
        if not names_to_delete:
            names_to_delete = self.names_to_delete

        orig = len(config.get("Tracks"))
        ids_remove = []

        for i, track in enumerate(config.get("Tracks")):
            track_name = track.get("stem_name").lower()
            if "drums" in track_name:
                logger_sel.warning("Drums protected")
                continue

            if any([name.lower() in track_name for name in names_to_delete]):
                ids_remove.append(i)

        for i in sorted(ids_remove, reverse=True):
            if not self.track_is_crutial(config, i):
                config.get("Tracks").pop(i)
            else:
                logger_sel.warning(
                    f'{config.get("Tracks")[i]["stem_name"]} '
                    "is crucial! SKIPPED"
                )

        final = len(config.get("Tracks"))
        return config, orig - final

    @staticmethod
    def add_times(config):
        """
        The function `add_times` calculates the total time for each track in
        a given configuration by reading a JSON file and summing the
        differences between the start and end times of each interval.

        :param config: The `config` parameter is a dictionary that contains
        information about a track. It has the following structure: :return:
        the updated `config` dictionary with the added "steps" and
        "total_time" keys for each track.
        """
        name = config.get("Name")
        for track in config.get("Tracks"):
            if not Path(track.get("steps_path")).exists():
                logger_sel.error(f"{name} - no Steps json")
                continue
            with open(track.get("steps_path"), "r") as js:
                time = 0
                data = json.load(js)
                if not isinstance(data, list):
                    logger_sel.error(f"{name} - Json in wrong format")
                    continue
                track["steps"] = data
                for interval in data:
                    try:
                        time += interval["endTime"] - interval["startTime"]
                    except KeyError:
                        logger_sel.error(
                            f"{name} - Keys not found for the " "interval"
                        )
                        continue
                track["total_time"] = round(time, 1)
        return config

    @staticmethod
    def tracks_time_ordered(config):
        """
        The function "tracks_time_ordered" takes a configuration dictionary
        as input and returns a list of track names and their corresponding
        total times, ordered by ascending total time.

        :param config: The `config` parameter is a dictionary that contains
        information about tracks. It has a key "Tracks" which maps to a list
        of dictionaries. Each dictionary in the list represents a track and
        contains keys "stem_name" and "total_time" :return: a list of
        tuples, where each tuple contains the stem name and total time of a
        track. The list is ordered in ascending order based on the total
        time of the tracks.
        """
        times = [
            (track.get("stem_name"), track.get("total_time"))
            for track in config.get("Tracks")
        ]
        times.sort(key=lambda x: x[1], reverse=False)
        return times
