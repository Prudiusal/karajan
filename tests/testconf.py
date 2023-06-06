import logging
import coloredlogs


# Here the logs are turned on
logging.basicConfig(level=logging.FATAL,
                    format='%(asctime)s - %(name)s - %(levelname)s'
                    ' %(message)s')

coloredlogs.install(level=logging.FATAL,
                    format='%(asctime)s - %(name)s - %(levelname)s'
                    ' %(message)s')

