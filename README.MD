This is an example of the use of dawdreamer to create the sound with different plugins.

You have to:
    - python 3.7 or later
    - DawDreamer module ('pip install dawdreamer');
    - tkinter.

If your system is not Windows, you have to wait for the repo update.

During the first run, the system will ask for the plugins paths and record them 
in the 'env.csv' file of project folder.

The 'demo' folder contains the folders for each channel of the track structure:
    - plugin preset name pattern '{position}_{plugin_name}.fxb';
    - the use of the plugin is defined by the presence of an appropriate preset; 
    - processing sequence is defined by the digits in the start of plugin name;
    - '.mid' file is processed by the plugin, which name starts on '0_'.

Have a fun!