import sys
import os
import io
import json
import unittest
from rich.console import Console

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import config
from src.modules.export.csv import saveToCsv
from src.modules.export.pdf import saveToPdf
from src.modules.export.file_operations import createSaveDirectory
from datetime import datetime

config.console = Console(file=io.StringIO())

config.no_nsfw = None
config.proxy = None
config.verbose = None
config.timeout = None
config.dump = None
config.currentUser = None
config.currentEmail = None
config.dateRaw = datetime.now().strftime("%m_%d_%Y")
config.datePretty = datetime.now().strftime("%B %d, %Y")


class TestExportToPDF(unittest.TestCase):
    config.currentEmail = "john@gmail.com"
    config.pdf = True
    config.csv = False
    createSaveDirectory(config)

    def test_export_pdf(self):
        with open(
            os.path.join(os.getcwd(), "tests", "data", "mock-email.json"),
            "r",
            encoding="UTF-8",
        ) as f:
            foundAccounts = json.load(f)
        result = saveToPdf(foundAccounts, "email", config)
        self.assertTrue(result)


class TestExportToCSV(unittest.TestCase):
    config.currentUser = "p1ngul1n0"
    config.pdf = False
    config.csv = True
    createSaveDirectory(config)

    def test_export_csv(self):
        with open(
            os.path.join(os.getcwd(), "tests", "data", "mock-username.json"),
            "r",
            encoding="UTF-8",
        ) as f:
            foundAccounts = json.load(f)
        result = saveToCsv(foundAccounts, config)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
