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
        if "Pink Cadillac" in config["Name"]:
            print()
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
        orig = len(config.get("Tracks"))
        tracks = [t for t in config["Tracks"] if t["total_time"] > 1]
        config["Tracks"] = tracks
        final = len(config.get("Tracks"))
        return config, orig - final

    def track_is_crutial(self, config, considering_index):
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
        periods = []
        for i, track in enumerate(config["Tracks"]):
            if i == exclude_index:
                continue
            periods.extend(track["steps"])
        return periods

    @staticmethod
    def merge_steps(periods):
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
        silence = 0
        init = 0
        for slot in timeslots:
            silence += slot["startTime"] - init
            init = slot["endTime"]
        return silence

    def remove_shortest(self, config, order, num_to_remove):
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
        times = [
            (track.get("stem_name"), track.get("total_time"))
            for track in config.get("Tracks")
        ]
        times.sort(key=lambda x: x[1], reverse=False)
        return times
