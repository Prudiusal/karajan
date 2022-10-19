This is an example of the use of dawdreamer to create the sound with different plugins with Python 3.7.

You have to:
    install DawDreamer module ('pip install dawdreamer');
    configure the paths to the installed plugins (rows 56-60).

If your system is not Windows, you have to wait for the repo update.

The 'demo' folder contains the folders for each channel of the track structure:
    - plugin preset name pattern '{position}_{plugin_name}.fxb';
    - the use of the plugin is defined by the presence of an appropriate preset; 
    - processing sequence is defined by the digits in the start of plugin name;
    - '.mid' file is processed by the plugin, which name starts on '0_'.

Have a fun!