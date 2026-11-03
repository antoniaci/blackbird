import os
import json
import requests
from pathlib import Path
from ..utils.log import logError
from ..utils.http_client import do_sync_request
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KEY_PATH = PROJECT_ROOT / ".ai_key.json"

def fetch_api_key_from_server(config):
    try:
        headers = {
            "User-Agent": "blackbird-cli",
        }
        response = do_sync_request(
            method="GET",
            url=config.api_url + "/generate-key",
            customHeaders=headers,
            config=config,
            data=None
        )
        
        data = response.json()

        if (data["success"]) and data["status"] == 200:
            apikey =  data["data"]["api_key"]
            config.console.print(f":white_check_mark: {data['message']}")
            save_api_key_to_file(apikey, config)
            return True
            

        if (data["status"] == 200 and not data["success"]):
            config.console.print(f":closed_lock_with_key: {data['message']}")
            if (data["data"] and "api_key" in data["data"]):
                apikey = data["data"]["api_key"]
                save_api_key_to_file(apikey, config)
                return True
        
        if (data["status"] == 500):
            config.console.print(f":x: {data['message']}")
            return None
            
        return None
    except Exception as e:
        logError(e, "Error obtaining API Key", config)
        return None

def save_api_key_to_file(api_key, config):
    try:
        with open(KEY_PATH, "w") as f:
            json.dump({"api_key": api_key}, f)
        config.console.print(f":white_check_mark: API Key saved to {KEY_PATH}")
    except Exception as e:
        config.console.print(":x: Error saving API Key to file!")
        logError(e, "Error saving API Key to file", None)

def load_api_key_from_file(config):
    if not KEY_PATH.exists():
        return None
    try:
        with open(KEY_PATH, "r") as f:
            data = json.load(f)
            if config.verbose:
                config.console.print(f":white_check_mark: API Key loaded from {KEY_PATH}")
            return data.get("api_key")
    except Exception as e:
        config.console.print(f":x: Error loading API Key {KEY_PATH}")
        logError(e, "Error loading API Key from file", None)
        return None