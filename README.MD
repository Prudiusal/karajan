This is an example of the use of dawdreamer to create the sound with different plugins.

### How to run:

1. Crete .env file by running the following command:
```shell
cat deploy/.env.example > .env
```
adjust the .env file; specify the paths to the plugins

2. Install required dependencies and run the app:
```shell
pipenv install
pipenv run python testVST.py
```

The 'demo' folder contains the folders for each channel of the track structure:
    - plugin preset name pattern '{position}_{plugin_name}.fxb';
    - the use of the plugin is defined by the presence of an appropriate preset; 
    - processing sequence is defined by the digits in the start of plugin name;
    - '.mid' file is processed by the plugin, which name starts on '0_'.

Have fun!
