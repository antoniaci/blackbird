from utils.http_client import do_sync_request
import time
import sys
from rich.text import Text
import json
from .key_manager import load_api_key_from_file
from utils.log import logError

def send_prompt(prompt, config, retries=3, announce=True):
    if announce:
        config.console.print(":sparkles: Analyzing with AI...")
    apikey = load_api_key_from_file(config)
    if not apikey:
        if announce:
            config.console.print(":x: No API key found. Please obtain an API key first with --setup-ai")
        return None
    headers = {"Content-Type": "application/json", "User-Agent": "blackbird-cli", "x-api-key": apikey}
    payload = json.dumps({"prompt": prompt})

    for attempt in range(retries):
        try:
            response = do_sync_request(method="POST", url=config.api_url + "/analyze", config=config, customHeaders=headers, data=payload)
            if response is None:
                raise ConnectionError("empty response")
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = None
            if response.status_code >= 500 and attempt < retries - 1:
                time.sleep(0.5 * (2 ** attempt))
                continue
            if response.status_code != 200:
                if data and announce:
                    config.console.print(f":x: {data['message']}")
                return None
            if data and data.get("success"):
                if announce:
                    show_results(data, config)
                return data["data"]["result"]
            return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5 * (2 ** attempt))
                continue
            if announce:
                config.console.print(":x: Error sending prompt to API!")
            logError(e, "Error sending prompt to API!", config)
            return None
    return None

def extract_data_with_ai(config, site, content, json_data):
    try:
        raw = json.dumps(json_data)[:6000] if json_data else str(content)[:6000]
        prompt = f"Analyze this {site['name']} profile data for OSINT insights: {raw}"
        result = send_prompt(prompt, config, announce=False)
        if not result:
            return []
        metadata = []
        if result.get("summary"):
            metadata.append({"schema": "AI", "type": "String", "name": "AI Summary", "value": result["summary"], "path": None})
        if result.get("categorization"):
            metadata.append({"schema": "AI", "type": "String", "name": "AI Category", "value": result["categorization"], "path": None})
        if result.get("tags"):
            metadata.append({"schema": "AI", "type": "String", "name": "AI Tags", "value": ", ".join(result["tags"]), "path": None})
        if result.get("risk_flags"):
            metadata.append({"schema": "AI", "type": "String", "name": "AI Risk Flags", "value": ", ".join(result["risk_flags"]), "path": None})
        if result.get("insights"):
            metadata.append({"schema": "AI", "type": "String", "name": "AI Insights", "value": ", ".join(result["insights"]), "path": None})
        return metadata
    except Exception as e:
        logError(e, f"AI metadata extraction failed for {site['name']}", config)
        return []

def show_results(results, config):
    ai_summary = results["data"]["result"]["summary"]
    ai_categorization = results["data"]["result"]["categorization"]
    ai_tags = results["data"]["result"]["tags"]
    ai_risk_flags = results["data"]["result"]["risk_flags"]
    ai_insights = results["data"]["result"]["insights"]
    remaining_quota = results["data"]["remaining_quota"]

    if ai_summary:
        type_block("Summary", ai_summary.strip().split("\n"), config)
    if ai_categorization:
        type_block("Profile Type", [ai_categorization], config)
    if ai_insights:
        type_block("Insights", [f"- {i}" for i in ai_insights], config)
    if ai_risk_flags:
        type_block("Risk Flags", [f"- {f}" for f in ai_risk_flags], config)
    if ai_tags:
        type_block("Tags", [", ".join(ai_tags)], config)
    config.console.print(f"{remaining_quota} AI queries left for today")

def type_line(line, delay=0.01):
    text = Text.assemble(("> ", "cyan1"), (line, "default"))
    for char in text.plain:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()
    time.sleep(0.05)

def type_block(title, content_lines, config):
    config.console.print(f"[[cyan1]{title}[/cyan1]]")
    for line in content_lines:
        type_line(f" {line}")
    print()
