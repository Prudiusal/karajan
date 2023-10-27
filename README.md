# Karajan Project Readme

## Overview
The Karajan project is a music rendering application that uses Python 3.10. This Readme provides instructions on how to set up and use the Karajan project via the command line. 

## Installation
1. Install Pipenv:
   - If you don't have Pipenv installed, you can do so by running the following command:
     ```
     pip install pipenv
     ```

2. Clone the Karajan project from its repository.

3. Navigate to the project directory in your terminal.

4. Create a virtual environment and install dependencies by running the following command:
   ```
   pipenv install
   ```

## Environment Configuration
You can configure the project's environment by modifying the `.env` file.

## Track, Plugin, and Preset Configuration
To define the parameters for rendering MIDI files, you can edit the `StylesConfig.json` file located in `./Resources/Configs/`.

## Rendering MIDI Files
There are two methods for rendering MIDI files:

### Method 1: Rendering Local Files
1. To render files located on your local disk, set the path in the `.env` file.

2. Run the following commands:
   ```
   pipenv shell
   python main.py -h
   python main.py --num-workers
   ```

3. Configuration files for each song will be created.

4. You will need to configure the plugin windows that open, after which the songs will be processed in parallel.

### Method 2: Running a Server
1. Launch a server that will accept MIDI files and render them, saving them locally.

2. Configure the plugin windows that open when the server starts.

3. Once configured, you can send POST requests with MIDI tracks to `localhost:8000/upload`.

   Example request format:
   ```
   POST /upload
   MIDI files for 4 tracks, track name, and BPM
   ```

   You can refer to `api_test.py` for an example request and use it to test the server.

   To test the server, open a new terminal and run:
   ```
   pipenv shell
   python api_test.py
   ```

4. Three tracks will be sent to the server for rendering.

## Running Tests
To run tests for the Karajan project, follow these steps:

1. Activate the virtual environment:
   ```
   pipenv shell
   ```

2. Run the tests using Pytest:
   ```
   pytest
   ```

That's it! You should now have the Karajan project up and running, allowing you to render MIDI files both locally and via a server. If you have any further questions or encounter issues, please consult the project's documentation or reach out to the project maintainers for assistance.