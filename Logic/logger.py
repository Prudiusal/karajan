import logging
import coloredlogs
import datetime as dt
from pathlib import Path


path_log = Path('.') / 'logs'
file_log = path_log / f'log_{dt.datetime.now().strftime("%d-%m-%y_%H:%M:%S")}.log'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s'
                    ' %(message)s')
                    # ' %(message)s', filename=file_log)

level_styles = {
    'debug': {'color': 'white'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'color': 'red', 'bold': True}
    }
coloredlogs.install(level=logging.DEBUG, level_styles=level_styles,
                    format='%(asctime)s - %(name)s - %(levelname)s'
                    ' %(message)s')

# coloredlogs.install(level=logging.INFO)
# coloredlogs.install(level=logging.WARNING)

logger_conf = logging.getLogger('config')

logger_midiVST = logging.getLogger('midiVST')

logger_render = logging.getLogger('renderEngine')

logger_main = logging.getLogger('main')

logger_VST = logging.getLogger('VST')

logger_track = logging.getLogger('Track')

logger_exc = logging.getLogger('exceptions')

