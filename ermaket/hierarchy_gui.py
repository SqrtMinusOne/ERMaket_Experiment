import logging.config
import sys

from PyQt5.QtWidgets import QApplication

from ermaket.api import Config
from ermaket.ui import HierachyEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = Config()
    logging.config.dictConfig({**config.Logging, **config.GUILogging})

    editor = HierachyEditor()
    editor.show()

    sys.exit(app.exec_())
