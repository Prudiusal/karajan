import logging

# import coloredlogs

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s'
                    ' %(message)s')

logger_conf = logging.getLogger('config')

logger_midiVST = logging.getLogger('midiVST')

logger_render = logging.getLogger('renderEngine')

logger_main = logging.getLogger('main')

logger_VST = logging.getLogger('VST')

logger_track = logging.getLogger('Track')

logger_exc = logging.getLogger('exceptions')
