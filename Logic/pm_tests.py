import pretty_midi


def get_mid_length(path, orig_bpm, req_bpm):
    """
    Checks the length of the midi file
    :param path: to the .mid file
    :return: time of the midi in seconds
    """
    req_bpm = int(req_bpm)
    orig_bpm = int(orig_bpm)
    pm = pretty_midi.PrettyMIDI(path)
    if len(pm.instruments) == 1:
        return pm.get_end_time() * orig_bpm / req_bpm
    elif len(pm.instruments) > 1:
        times = [track.get_end_time() for track in pm.instruments]
        return max(times) * orig_bpm / req_bpm
