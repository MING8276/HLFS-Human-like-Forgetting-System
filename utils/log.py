import logging
from utils.tools import makeFile

"""
create a logger
"""



class Logs(object):

    def __init__(self, loggerName: str, filePath: str = None):
        self.logger = logging.getLogger(loggerName)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if filePath is None:
            handler = logging.StreamHandler()
        else:
            makeFile(filePath)
            handler = logging.FileHandler(filePath, encoding='utf-8')
        self.logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)


dialog_logger = Logs('dialog', '../logs/dialog.log')
summary_logger = Logs('summary', '../logs/summary.log')
topic_logger = Logs('topic', '../logs/topic.log')
personality_logger = Logs('personality', '../logs/personality.log')
prefetch_logger = Logs('prefetch', '../logs/prefetch.log')