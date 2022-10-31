# Learn with music - site that allows to download music and play & learn with its lyrics.

## Lots of useful features can be implemented, but for now, just these are implemented as an MVP only

. Download of video using given Youtube url  
. Download of subtitles using given Youtube video url(other sources support will be added later)  
. After previous steps(if we had 1 or 2 videos one of which had subtitles added) we can listen to song and view what is mentioned in each line when playing song at the same time

# important todos so far

. make code cleaner when it becomes clear that specific features will remain this way for now  
. add pydantic models/dataclasses for important functionality, ex: use something like LyricsLine object with all required fields to pass between functions, instead of doing validations by hand and relying on passer functions. This will allow for example to create same LyricsLine object by supplying start time and duration, or start time and end times, so that we do not need to care about those details later on, we will always have data we need.

. Fix and add more tests  
. Add better handling of subtitles/lyrics storage, as current one seems to be very slow for medium/large scale  
. store not one language of captions, but multiple(probably all available in youtube video for example). currently just first one is stored and for example if we are playing non english song, we can listen to other language song text in English translations in live, but in some cases this may not be what we want, so when making changes in subtitles storage, make sure this bullet point is remembered
