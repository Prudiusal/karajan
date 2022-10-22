from os import environ

from dotenv import load_dotenv

load_dotenv()

SAMPLE_RATE = int(environ.get('SAMPLE_RATE', 44100))
BUFFER_SIZE = int(environ.get('BUFFER_SIZE', 128))

# Python on Windows will automatically handle forward slashes (/) properly;
# or you can simple use '\\' instead.
SERUM_PATH = environ.get('SERUM_PATH', 'C:/Program Files/Common Files/VST2/ValhallaSupermassive_x64.dll')
VALHALLAFREQ_PATH = environ.get('VALHALLAFREQ_PATH', 'C:/vstplugins/ValhallaFreqEcho_x64.dll')
VALHALLASUPER_PATH = environ.get('VALHALLASUPER_PATH', 'C:/Program Files/Common Files/VST2/ValhallaSupermassive_x64.dll')
