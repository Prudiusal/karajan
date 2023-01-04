import pretty_midi


def check_length(path):
    pm = pretty_midi.PrettyMIDI(path)
    if len(pm.instruments) == 1:
        return pm.get_end_time()
    elif len(pm.instruments) > 1:
        times = [track.get_end_time() for track in pm.instruments]
        return max(times)
