import asyncio, logging, aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
from database import db
from configs import *
from aiohttp import web
from pyrogram import enums, Client
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from urllib.parse import urlparse
from pyrogram import filters

message_lock = asyncio.Lock()


executor = ThreadPoolExecutor()


async def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(executor, requests.get, url, headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None


def get_size_in_bytes(size_str):
    size_str = size_str.lower()
    size_match = re.search(r"([\d.]+)\s*(gb|mb)", size_str)
    if size_match:
        size_value = float(size_match.group(1))
        size_unit = size_match.group(2)
        if size_unit == "gb":
            return size_value * 1024 * 1024 * 1024
        elif size_unit == "mb":
            return size_value * 1024 * 1024
    return None


async def parse_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for link in soup.find_all("a", href=True):
        if "/index.php?/forums/topic/" in link["href"]:
            if link["href"] not in links:
                links.append(link["href"])

            if len(links) == 20:
                break

    return links


async def fetch_attachments(page_url):
    html = await fetch(page_url)
    if not html:
        return None

    # Regex for episode and non-episode links
    episode_pattern = re.compile(r"E(?:P)?(\d{1,2})", re.IGNORECASE)
    non_episode_regex = re.compile(
        r"S(\d{1,2})\s*(?:E|EP)?\s*\(?(\d+(?:-\d+))\)?", re.IGNORECASE
    )

    # Regex to clean link text
    domain_removal_regex = re.compile(r"\b(www\.[^\s/$.?#].[^\s]*)\b")
    mkv_torrent_removal_regex = re.compile(r"\.mkv\.torrent$")

    title_domain_removal_regex = re.compile(
        r"\b(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})\b"
    )

    soup = BeautifulSoup(html, "html.parser")

    links = []

    content_div = soup.find("div", class_="cPost_contentWrap")
    img_url = None
    if content_div:
        img_tag = content_div.find("img")
        if img_tag and img_tag.get("src"):
            img_url = img_tag["src"]

    highest_episode_number = 0
    highest_episode_links = []
    season_based_links = []

    # Initialize variables for highest season tracking
    highest_season = 0
    highest_episode_range = (
        0,
        0,
    )  # Tuple to store the start and end of the highest episode range

    # Loop through all the 'a' tags to find attachment.php links
    for link in soup.find_all("a", href=True):
        if "attachment.php" in link["href"]:
            # Fetch file size
            size_tag = link.find_next(
                "span", string=re.compile(r"\d+(?:\.\d+)?\s*(?:GB|MB)", re.I)
            )
            size_in_bytes = get_size_in_bytes(size_tag.text) if size_tag else None

            # Clean the link text
            link_text = link.get_text(strip=True)
            clean_link_text = domain_removal_regex.sub("", link_text)
            clean_link_text = mkv_torrent_removal_regex.sub("", clean_link_text).strip()

            # Modify this section to handle episode ranges
            season_match = non_episode_regex.search(link_text)
            if season_match:
                season_number = int(season_match.group(1))
                episode_range = season_match.group(2)

                # Split the range into start and end episodes if it's a range like 25-27
                if "-" in episode_range:
                    episode_start, episode_end = map(int, episode_range.split("-"))
                else:
                    episode_start = episode_end = int(episode_range)

                # Check if this season and episode range is higher than the current highest
                if season_number > highest_season or (
                    season_number == highest_season
                    and episode_end > highest_episode_range[1]
                ):
                    highest_season = season_number
                    highest_episode_range = (episode_start, episode_end)
                    season_based_links = [
                        {"name": clean_link_text, "link": link["href"]}
                    ]
                elif (
                    season_number == highest_season
                    and episode_start <= highest_episode_range[1]
                ):
                    season_based_links.append(
                        {"name": clean_link_text, "link": link["href"]}
                    )

            # Step 2: Check for episode-specific links (only allow < 4GB)
            episode_matches = episode_pattern.findall(link_text)
            if episode_matches and size_in_bytes is not None:
                current_episode_number = max(int(ep) for ep in episode_matches)
                if size_in_bytes < 4 * 1024 * 1024 * 1024:  # Only include < 4GB
                    if current_episode_number > highest_episode_number:
                        highest_episode_number = current_episode_number
                        highest_episode_links = [
                            {"name": clean_link_text, "link": link["href"]}
                        ]
                    elif current_episode_number == highest_episode_number:
                        highest_episode_links.append(
                            {"name": clean_link_text, "link": link["href"]}
                        )

            # Step 3: Check for non-episode links (only allow < 4GB)
            elif size_in_bytes is not None and size_in_bytes < 4 * 1024 * 1024 * 1024:
                links.append({"name": clean_link_text, "link": link["href"]})

    # Combine all valid links (season-based first, then episode links, then non-episode)
    final_links = (
        season_based_links
        if season_based_links
        else (highest_episode_links if highest_episode_links else links)
    )

    document = {
        "img_url": img_url,
        "links": final_links,
        "added_on": datetime.utcnow(),
    }

    await db.add_document(document)
    return document


async def start_processing():
    main_page_html = await fetch(BASE_URL)

    if main_page_html:
        fetched_links = await parse_links(main_page_html)

        for li_link in fetched_links:
            logging.info(f"Fetching attachments from {li_link}")
            await fetch_attachments(li_link)

    else:
        logging.warning("No content found on the main page!")


routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("MadxBotz")


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app


User = Client(
    "User", session_string=USER_SESSION_STRING, api_hash=API_HASH, api_id=API_ID
)


async def ping_server():
    while True:
        try:
            await start_processing()
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
        await asyncio.sleep(60)


async def ping_main_server():
    try:
        await User.start()
        logging.info("User Session started.")
        await User.send_message(GROUP_ID, "User Session Started")
    except Exception as e:
        logging.error(f"Error Starting User: {str(e)}")

    while True:
        await asyncio.sleep(250)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(SERVER_URL) as resp:
                    logging.info("Pinged server with response: {}".format(resp.status))
        except TimeoutError:
            logging.warning("Couldn't connect to the site URL.")
        except Exception:
            traceback.print_exc()


async def stop_user():
    await User.send_message(GROUP_ID, "User Session Stopped")
    await User.stop()
    logging.info("User Session Stopped.")
    