This project allows to create the new song, using styles and songs descriptions.

Styles description is stored in ./Resources/Configs/StyleConfig.json and contain information about bpm, tracks, plugins, presets.
Songs description are stored in ./Resources/Configs/StyleConfig.json and contain the paths for midi files of the song tracks.

How to run: 
Install required dependencies and run the app:
pipenv install
pipenv shell
python3 Logic/main.py

**Right now there is no choice of song and style being used, so those params are hard-coded.