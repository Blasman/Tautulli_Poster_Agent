# Tautulli Poster Agent

**Update [2024_11_01]**: It's worth noting that I have learned that the Tautulli dev (JonnyWong16) has created a [similar script](https://gist.github.com/JonnyWong16/b0e6b2761f8649d811f51866e682464b) that I believe does what this script does. I would recommend that script first, as it is likely to be maintained whereas this script will no longer be updated as I no longer have a use for either script. Replacing posters on movies has become part of my [Plexato](https://github.com/Blasman/Plexato) script logic as it makes more sense to replace posters going from Radarr to Plex rather than Tautulli to Plex (no delay, more control).

Tautulli Poster Agent (aka TPA) is a [Tautulli](https://github.com/Tautulli/Tautulli) custom script to effectively "replace" [Plex's failing movie poster agent](https://forums.plex.tv/t/once-upon-a-time-in-the-west-metadata/852193). TPA uses direct links to TMDB and/or IMDb for poster images to replace the current poster image for 'Recently Added' movies. The functionality is the same as the 'enter a URL' option when editing a poster image via the Plex Web UI.

There is also an **optional** user config within the script where you can set your [TMDB API KEY](https://www.themoviedb.org/settings/api) to enable the TMDB API lookup method. The TMDB API lookup method is theoretically more reliable than the other URL lookup methods (website designs change).

There are currently *three* lookup methods. The lookup methods and default search order in the user config are: `TMDB API` `TMDB URL` `IMDb`. If selecting more than one lookup method, then the additional methods as used as fallbacks. 

TPA runs *after* Plex downloads its own poster for the new movie. By default, Tautulli's 'Recently Added Notification Delay' is set to 300 seconds. If you want posters uploaded sooner, then I recommended lowering this number. It goes as low as 60 seconds.

## Installation

```
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
```
