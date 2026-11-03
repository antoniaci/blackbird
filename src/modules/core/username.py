import sys
import os
import time
import aiohttp
import asyncio

from rich.live import Live
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)

from ..whatsmyname.list_operations import readList
from ..utils.parse import extractMetadata, remove_duplicates
from ..utils.filter import filterFoundAccounts, applyFilters
from ..utils.http_client import do_async_request
from ..utils.log import logError
from ..export.dump import dumpContent
from ..sites.instagram import get_instagram_account_info
from ..ai.client import extract_data_with_ai

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Verify account existence based on list args
async def checkSite(
    site,
    method,
    url,
    session,
    semaphore,
    config,
    data=None,
    headers=None,
):
    returnData = {
        "name": site["name"],
        "url": url,
        "category": site["cat"],
        "status": "NONE",
        "metadata": None,
    }
    extractedMetadata = []

    async with semaphore:
        response = await do_async_request(
            method, url, session, config, data=data, customHeaders=headers
        )
        if response == None:
            returnData["status"] = "ERROR"
            return returnData
        try:
            if response:
                if (site["e_string"] in response["content"]) and (
                    site["e_code"] == response["status_code"]
                ):
                    if (site["m_string"] not in response["content"]) and (
                        (site["m_code"] != response["status_code"])
                        if site["m_code"] != site["e_code"]
                        else True
                    ):
                        returnData["status"] = "FOUND"
                        config.console.print(
                            rf"  ✔️  \[[cyan1]{site['name']}[/cyan1]] [bright_white]{response['url']}[/bright_white]"
                        )

                        if site["name"] in config.metadata_params["sites"]:
                            metadata = extractMetadata(
                                config.metadata_params["sites"][site["name"]],
                                response,
                                site["name"],
                                config,
                            )
                            extractedMetadata.extend(metadata)

                        if config.ai and config.aiModel:
                            metadata = extract_data_with_ai(
                                config, site, response["content"], response["json"]
                            )
                            extractedMetadata.extend(metadata)

                        if site["name"] == "Instagram":
                            if config.instagram_session_id:
                                metadata = get_instagram_account_info(
                                    config.currentUser,
                                    config.instagram_session_id,
                                    config,
                                )
                                extractedMetadata.sort(key=lambda x: x["name"])
                                extractedMetadata.extend(metadata)

                        if extractedMetadata and len(extractedMetadata) > 0:
                            extractedMetadata = remove_duplicates(extractedMetadata)
                            extractedMetadata.sort(key=lambda x: x["name"])
                            returnData["metadata"] = extractedMetadata

                        # Save response content to a .HTML file
                        if config.dump:
                            path = os.path.join(
                                config.saveDirectory, f"dump_{config.currentUser}"
                            )

                            result = dumpContent(path, site, response, config)
                            if result == True and config.verbose:
                                config.console.print(
                                    f"      💾  Saved HTML data from found account"
                                )
                else:
                    returnData["status"] = "NOT-FOUND"
                    if config.verbose:
                        config.console.print(
                            f"  ❌ [[blue]{site['name']}[/blue]] [bright_white]{response['url']}[/bright_white]"
                        )
                return returnData
        except Exception as e:
            logError(e, f"Coudn't check {site['name']} {url}", config)
            return returnData


from rich.live import Live
from rich.console import Group
from rich.text import Text

async def fetchResults(username, config):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        total_sites = len(config.username_sites)
        completed = 0
        results = []

        def render():
            percent = int((completed / total_sites) * 100)
            return Text.from_markup(
                f"🛰️  Enumerating accounts with username [cyan1]\"{username}\"[/cyan1] — [green1]{percent}%[/green1] ({completed}/{total_sites})"
            )

        async def wrappedCheck(site):
            nonlocal completed
            account = username
            for char in site.get("strip_bad_char", ""):
                account = account.replace(char, "")
            postBody = site.get("post_body")
            result = await checkSite(
                site=site,
                method="POST" if postBody else "GET",
                url=site["uri_check"].replace("{account}", account),
                session=session,
                semaphore=semaphore,
                config=config,
                data=postBody.replace("{account}", account) if postBody else None,
                headers=site.get("headers"),
            )
            completed += 1
            return result

        tasks = [wrappedCheck(site) for site in config.username_sites]

        with Live(render(), refresh_per_second=10, console=config.console) as live:
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                live.update(render())

        return {"results": results, "username": username}




# Start username check and presents results to user
def verifyUsername(username, config, sitesToSearch=None, metadata_params=None):
    if sitesToSearch is None or metadata_params is None:
        data = readList("username", config)
        sitesToSearch = data["sites"]
        config.metadata_params = readList("metadata", config)
    else:
        config.metadata_params = metadata_params

    config.username_sites = applyFilters(sitesToSearch, config)

    start_time = time.time()
    results = asyncio.run(fetchResults(username, config))
    end_time = time.time()

    config.console.print(
        f":chequered_flag: Check completed in {round(end_time - start_time, 1)} seconds"
    )

    if config.dump:
        config.console.print(
            f"💾  Dump content saved to '[cyan1]{config.currentUser}_{config.dateRaw}_blackbird/dump_{config.currentUser}[/cyan1]'"
        )

    # Filter results to only found accounts
    foundAccounts = list(filter(filterFoundAccounts, results["results"]))
    config.usernameFoundAccounts = foundAccounts
    if len(foundAccounts) <= 0:
        config.console.print("⭕ No accounts were found for the given username")

    return foundAccounts
