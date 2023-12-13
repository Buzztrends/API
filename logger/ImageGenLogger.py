import logging
from logging.handlers import RotatingFileHandler

class ImageGenLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger("ImageGenLogger")
        self.logger.setLevel(logging.INFO)
        
        #================ Formatter ================
        self.fomartter = logging.Formatter(fmt="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                                           datefmt="%B %d, %Y %H:%M:%S %Z")
        
        #================ Setting Up File Handler===
        self.file_handler = RotatingFileHandler("./logs/ImageGenLogs.log",
                                                maxBytes=1000000,
                                                backupCount=5)
        self.file_handler.setFormatter(self.fomartter)
        self.file_handler.setLevel(10)
        self.logger.addHandler(self.file_handler,)
        #================ Setting Up Console========
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.fomartter)
        self.console_handler.setLevel(30)
        self.logger.addHandler(self.console_handler)
    def getLogger(self):
        return self.logger