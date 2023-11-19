#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Poster Agent

Replaces the poster image for 'Recently Added' movies with a poster image directly from TMDB or IMDb.
Functionality is the same as the 'enter a URL' option to change the poster in Plex via the web client.

Enabling Scripts in Tautulli:
Taultulli > Settings > Notification Agents > Add a Notification Agent > Script

Configuration:
Taultulli > Settings > Notification Agents > New Script > Configuration:
 
 Script Folder: /path/to/your/scripts
 Script File: poster_agent.py
 Script Timeout: 40  (keep this higher than 'PROCESSING_DELAY' variable!)
 Description: Poster Agent
 Save

Triggers:
Taultulli > Settings > Notification Agents > New Script > Triggers:

 Check: Recently Added
 Save

Conditions:
Taultulli > Settings > Notification Agents > New Script > Conditions:

 Set desired Conditions and Condition Logic. 'Media Type' is 'movie'. Optionally 'Library Name' etc.
 Save

Script Arguments:
Taultulli > Settings > Notification Agents > New Script > Script Arguments:

 Select: Notify on Recently Added
 Arguments: --media_type {media_type} --title "{title}<movie> [{year}]</movie>" --tmdb_id {themoviedb_id} --tmdb_url {themoviedb_url} --imdb_url {imdb_url} --library {library_name} --guid {guid} --start_time {unixtime}

 Save
 Close
"""

import sys
import requests
import time
import os
import argparse
import re
from plexapi.server import PlexServer

################################################################################
#                            *OPTIONAL* USER CONFIG                            #
################################################################################
# Choose as many lookup methods as desired in order of preference. Additional methods are used as fallbacks.
LOOKUP_METHODS = ('tmdb_api', 'tmdb_url', 'imdb')  # Valid values: 'tmdb_api', 'tmdb_url', 'imdb'
# OPTIONALLY provide your TMDB API KEY. Required for 'tmdb_api' lookup method. Uncomment line below to use.
#TMDB_APIKEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # https://www.themoviedb.org/settings/api
# Set the image quality of the posters from TMDB.
TMDBPOSTER_QUALITY = 'original'  # Valid values: 'original' 'w780' 'w500' 'w342' 'w185' 'w154' 'w92'
# Delay the upload of the poster to Plex by X seconds from Tautulli's 'Recently Added' notification.
PROCESSING_DELAY = 5  # This delay is *in addition* to Tautulli's 'Recently Added Notification Delay' setting.
###############################################################################
#                             END OF USER CONFIG                              #
###############################################################################

# Global Variables.
PLEX_URL = ''
PLEX_TOKEN = ''
PLEX_URL = os.getenv('PLEX_URL', '')
PLEX_TOKEN = os.getenv('PLEX_TOKEN', '')
POSTER_URL = None
HEADERS = {'Cache-Control': 'no-cache',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}

# TMDB API lookup method.
def tmdb_api_lookup():
    global POSTER_URL
    tmdb_media_type = ''
    if opts.media_type == 'movie': tmdb_media_type='movie'
  # elif opts.media_type == 'show': tmdb_media_type='tv'  # Possible future use for tv shows.
    tmdb_search_url = f'https://api.themoviedb.org/3/{tmdb_media_type}/{opts.tmdb_id}?api_key={TMDB_APIKEY}'
    try:
        response = requests.get(tmdb_search_url)
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data:
            POSTER_URL = 'https://image.tmdb.org/t/p/' + TMDBPOSTER_QUALITY + data['poster_path']
            sys.stdout.write("[MATCH FOUND] TMDB poster image found (API lookup).\n")
            return True
        else: sys.stderr.write("[ERROR] No 'poster_path' found in the response from TMDB API.\n")
    except requests.RequestException as e:
        if 'Unauthorized' in str(e): sys.stderr.write(f"[ERROR] Invalid TMDB API KEY. Error: {e}\n")
        else: sys.stderr.write(f"[ERROR] Could not connect to TMDB API. Error: {e}\n")

# TMDB URL lookup method.
def tmdb_url_lookup():
    global POSTER_URL
    response = requests.get(opts.tmdb_url, headers=HEADERS)
    if response.status_code == 200:
        filename_match = re.search(r'/t/p/w.*?(/.*?\..*?)">', response.text)
        if filename_match:
            POSTER_URL = 'https://image.tmdb.org/t/p/' + TMDBPOSTER_QUALITY + filename_match.group(1)
            sys.stdout.write("[MATCH FOUND] TMDB poster image found (URL lookup).\n")
            return True
        else: sys.stderr.write("[ERROR] Unable to extract filename from TMDB URL.\n")
    else: sys.stderr.write(f"[ERROR] Failed to retrieve TMDB page. Status code: {response.status_code}\n")

# IMDb URL lookup method.
def imdb_lookup():
    global POSTER_URL
    response = requests.get(opts.imdb_url, headers=HEADERS)
    if response.status_code == 200:
        url_match = re.search(r'"image":"(https://[^"]+)"', response.text)
        if url_match:
            POSTER_URL = url_match.group(1)
            sys.stdout.write("[MATCH FOUND] IMDb poster image found.\n")
            return True
        else: sys.stderr.write("[ERROR] Unable to extract filename from IMDb URL.\n")
    else: sys.stderr.write(f"[ERROR] Failed to retrieve IMDb page. Status code: {response.status_code}\n")

# Upload the poster to Plex.
def upload_poster_to_plex():
    elapsed_time = time.time() - opts.start_time
    if elapsed_time < PROCESSING_DELAY: time.sleep(PROCESSING_DELAY - elapsed_time)
    plexapi = PlexServer(PLEX_URL, PLEX_TOKEN)
    movie = plexapi.library.section(opts.library).getGuid(opts.guid)
    if movie:
        try:
            upload_success = movie.uploadPoster(url=POSTER_URL)
            if upload_success: sys.stdout.write("[UPLOAD SUCCESS] Uploaded poster image to Plex.\n")
            else: sys.stderr.write("[ERROR] Failed to upload the poster to Plex.\n")
        except Exception as e: sys.stderr.write(f"[ERROR] {e}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--media_type', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--tmdb_id', required=True)
    parser.add_argument('--tmdb_url', required=True)
    parser.add_argument('--imdb_url', required=True)
    parser.add_argument('--library', required=True)
    parser.add_argument('--guid', required=True)
    parser.add_argument('--start_time', required=True, type=int)
    opts = parser.parse_args()
    # Verify that the item is a movie. Possible future use for 'shows'. (movie|show).
    if opts.media_type == 'movie':
        sys.stdout.write(f"[SEARCH STARTED] {opts.library}: '{opts.title}'\n")
        for method in LOOKUP_METHODS:
            if method.lower() == 'tmdb_api' and 'TMDB_APIKEY' in globals() and tmdb_api_lookup(): break
            elif method.lower() == 'tmdb_url' and tmdb_url_lookup(): break
            elif method.lower() == 'imdb' and imdb_lookup(): break
        if POSTER_URL: upload_poster_to_plex()
        else: sys.stderr.out("[SEARCH FAILED] COULD NOT FIND A POSTER.\n")
