import csv
import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)

from ..export.file_operations import generateName
from ..utils.log import logError


def _flatten_metadata(metadata):
    for m in metadata or []:
        if isinstance(m, list):
            yield from m
        elif isinstance(m, dict):
            yield m


def saveToCsv(results, config):
    try:
        fileName = generateName(config, "csv")
        path = os.path.join(config.saveDirectory, fileName)
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "url", "category", "status", "metadata"])
            for result in results:
                flat = "; ".join(f"{m['name']}: {m.get('value', '')}" for m in _flatten_metadata(result.get("metadata")) if m.get("value"))
                writer.writerow([result["name"], result["url"], result.get("category", ""), result.get("status", ""), flat])
        config.console.print(f"💾  Saved results to '[cyan1]{fileName}[/cyan1]'")
        return True
    except Exception as e:
        logError(e, "Coudn't saved results to CSV file!", config)
        return False
