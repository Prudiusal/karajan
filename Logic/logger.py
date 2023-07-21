import logging
import coloredlogs
import datetime as dt
from pathlib import Path
import settings as cfg


LEVEL = logging.INFO

# path_log = Path('.') / 'logs'
path_log = Path(cfg.LOG_PATH)
path_log.mkdir(exist_ok=True, parents=True)
file_log_name = f'log_{dt.datetime.now().strftime("%d-%m-%y_%H:%M:%S")}.log'
file_log = path_log / file_log_name

logging.basicConfig(level=LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s'
                    ' %(message)s', filename=file_log)

level_styles = {
    'debug': {'color': 'white'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'color': 'red', 'bold': True}
    }
coloredlogs.install(level=LEVEL, level_styles=level_styles,
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

logger_sel = logging.getLogger('selector')
