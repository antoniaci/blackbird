import sys
import os
import json
from datetime import datetime, timezone

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)

from ..export.file_operations import generateName
from ..utils.log import logError


def saveToJson(results, config):
    try:
        fileName = generateName(config, "json")
        path = os.path.join(config.saveDirectory, fileName)
        categories = {}
        for r in results:
            key = r.get("category", "Unknown")
            categories[key] = categories.get(key, 0) + 1
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_found": len(results),
            "by_category": categories,
            "results": results,
        }
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=4)
        config.console.print(f"💾  Saved results to '[cyan1]{fileName}[/cyan1]'")
        return True
    except Exception as e:
        logError(e, "Couldn't save results to JSON file!", config)
        return False
