# Local Riding Events: Okanagan Political & Civic Calendar

A calendar feed of political, civic, charity, NGO and community events in **Okanagan Lake West—South Kelowna** (MP Dan Albas: West Kelowna, Westbank First Nation, Peachland, Summerland, South Kelowna) and the **City of Kelowna**.

## Subscribe in Outlook

Feed URL:

```
https://raw.githubusercontent.com/AmarKhaira02/LocalRidingEvents/main/calendar.ics
```

- **Outlook (web / new Outlook):** Calendar → Add calendar → Subscribe from web → paste URL → name it → Import.
- **Classic Outlook (Windows):** Home → Add Calendar → From Internet → paste URL.

Outlook checks for changes by itself every few hours.

## How it's maintained

- `events.json` is the source of truth. Each event has `id`, `cat`, `title`, `start`, `end` (local Kelowna time) or `allday`, `location`, `desc` and `url`.
- `build_ics.py` turns it into `calendar.ics`: `python3 build_ics.py events.json calendar.ics`
- A weekly scheduled task researches new events, updates `events.json`, rebuilds the feed and commits it.
- Times are written in UTC, converted from America/Vancouver using current tz data. BC has been on permanent UTC−7 since Nov 1, 2026.

## Categories

Municipal Government · Regional Government · Committees & Advisory Bodies · Federal & Provincial Politics · Business & Economic Policy · Charity & Fundraisers · Community & NGO · Indigenous & First Nations · Ceremonies & Commemorations · Education & Public Lectures
