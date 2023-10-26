import datetime as dt
import multiprocessing
from argparse import ArgumentParser
from pathlib import Path
from uuid import uuid4

from flask import Flask, request  # , flash

from Logic import ServerRunner, logger_api


queue = multiprocessing.JoinableQueue()
now = dt.datetime.now().strftime("%d-%m-%y_%H-%M-%S")
output_path = f"./WAVs/api_rendering_{now}/"
Path(output_path).mkdir(exist_ok=True, parents=True)
tmp_path = Path(".") / "tmp" / "midi_api"
tmp_path.mkdir(exist_ok=True, parents=True)
# queue = Queue()
# ----------------------------------
# Flask

app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload_midi_files():
    """
    This functions recieves a request with midi files
    It tries to get midi files and save them in './tmp' dir
    Then the configutations is extended with some additional parameters
    Finally the SongConfig object is created and sent to queue
    """

    name = request.form["name"]
    bpm = request.form["bpm"]
    piano_midi = request.files["piano_midi"]
    piano_path = tmp_path / (str(uuid4()) + ".mid")
    piano_midi.save(piano_path.absolute())

    drums_midi = request.files["drums_midi"]
    drums_path = tmp_path / (str(uuid4()) + ".mid")
    drums_midi.save(drums_path.absolute())

    strings_midi = request.files["strings_midi"]
    strings_path = tmp_path / (str(uuid4()) + ".mid")

    strings_midi.save(strings_path.absolute())

    bass_midi = request.files["bass_midi"]
    bass_path = tmp_path / (str(uuid4()) + ".mid")
    bass_midi.save(bass_path.absolute())

    config = {
        "Name": name,
        "Artist": "",
        "OutputPath": output_path,
        "BPM": int(bpm),
        "Tracks": [
            {"track_name": "Drums", "tmp_midi_path": str(drums_path)},
            {"track_name": "Piano", "tmp_midi_path": str(piano_path)},
            {"track_name": "Strings", "tmp_midi_path": str(strings_path)},
            {"track_name": "Bass", "tmp_midi_path": str(bass_path)},
        ],
    }
    queue.put(config)
    logger_api.info(f"{name} has received and sent to processing")
    return f"{name} has received and sent to processing"

    # try:
    #     bpm = request.form['bpm']
    # except BadRequestKeyError as e:
    #     print(e)
    #     bpm = None
    # try:
    #     drums_midi = request.files['drums_midi']
    #     drums_path = tmp_path / (str(uuid4()) + '.mid')
    #     drums_midi.save(drums_path.absolute())
    # except BadRequestKeyError as e:
    #     print(e)
    #     drums_path = None
    # try:
    #     piano_midi = request.files['piano_midi']
    #     piano_path = tmp_path / (str(uuid4()) + '.mid')
    #     piano_midi.save(piano_path.absolute())
    # except BadRequestKeyError as e:
    #     print(e)
    #     piano_path = None
    # try:
    #     strings_midi = request.files['strings_midi']
    #     strings_path = tmp_path / (str(uuid4()) + '.mid')
    #     strings_midi.save(strings_path.absolute())
    # except BadRequestKeyError as e:
    #     print(e)
    #     strings_path = None
    # try:
    #     bass_midi = request.files['bass_midi']
    #     bass_path = tmp_path / (str(uuid4()) + '.mid')
    #     bass_midi.save(bass_path.absolute())
    # except BadRequestKeyError as e:
    #     print(e)
    #     bass_path = None


if __name__ == "__main__":
    parser = ArgumentParser(description="Rendering server for midi")
    parser.add_argument(
        "--num-workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of process for rendering (default: CPU count)",
    )
    args = parser.parse_args()
    num_workers = args.num_workers
    logger_api.info(f"{num_workers} workers are used to render.")
    runner = ServerRunner(queue, num_workers)
    runner.run_engines()
    app.run(host="0.0.0.0", port=8000)
