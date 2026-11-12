# Local Riding Events: Okanagan Political & Civic Calendar

A calendar feed of political, civic, charity, NGO and community events in **Okanagan Lake West—South Kelowna** (MP Dan Albas: West Kelowna, Westbank First Nation, Peachland, Summerland, South Kelowna) and the **City of Kelowna**.

## Subscribe in Outlook

Feed URL:

```
https://raw.githubusercontent.com/AmarKhaira02/LocalRidingEvents/main/calendar.ics
```

- **Outlook (web / new Outlook):** Calendar → Add calendar → Subscribe from web → paste URL → name it → Import.
- **Classic Outlook (Windows):** Home → Add Calendar → From Internet → paste URL.

Outlook checks for changes by itself every few hours (the feed asks for a refresh every 6 hours).

## How it's maintained

- `events.json` is the source of truth. `build_ics.py` turns it into `calendar.ics`: `python3 build_ics.py events.json calendar.ics`
- A **daily** scheduled task (early morning, Kelowna time) researches new events, updates `events.json`, rebuilds the feed and commits it when something changed.
- Times are written in UTC, converted from America/Vancouver using current tz data. BC has been on permanent UTC−7 since Nov 1, 2026.
- Each event's `id` stays stable so Outlook updates events in place instead of duplicating them.

## Event fields

| Field | Required | Notes |
|---|---|---|
| `id`, `title`, `location`, `desc`, `url` | yes | `location` includes the full street address; `desc` is 2–4 sentences on what happens |
| `start`, `end` or `allday` | yes | Local Kelowna time, `YYYY-MM-DDTHH:MM`, or `"allday": true` with date-only values |
| `cat` | yes | One broad category (below) |
| `type` | yes | Specific event type; shown in the title prefix |
| `jurisdiction` | yes | Which government or community it belongs to; shown in the title prefix |
| `riding` | when known | Federal riding: `Okanagan Lake West—South Kelowna` or `Kelowna` |
| `tags` | yes | Any number of tags from the list below |
| `gr_note` | recommended | Why it matters for government relations |
| `organizer`, `attendees`, `cost`, `access`, `registration`, `livestream`, `agenda`, `contact` | whenever known | Shown under DETAILS in Outlook |
| `unconfirmed` | when needed | Anything not yet confirmed (time, venue, etc.) |

In Outlook, each event title reads `[Type · Jurisdiction] Title`, and the description is laid out as WHEN, WHERE, CATEGORY/TYPE/JURISDICTION/RIDING/TAGS, ABOUT, WHY IT MATTERS, DETAILS, NOT YET CONFIRMED and SOURCE. All tags are also written to the event's categories.

The build stops with an error if an event uses a category, type, jurisdiction or tag that isn't in the lists in `build_ics.py`, so the vocabulary stays consistent. Add new values there first.

## Categories

Municipal Government · Regional Government · Committees & Advisory Bodies · Federal & Provincial Politics · Business & Economic Policy · Charity & Fundraisers · Community & NGO · Indigenous & First Nations · Ceremonies & Commemorations · Education & Public Lectures

## Types

Council Meeting · Public Hearing · Inaugural Meeting · Committee of the Whole · Budget Meeting · Board Meeting · Advisory Committee · Town Hall · Party Event · Nomination Meeting · AGM · Candidate Forum · Open House · Public Consultation · Protest / Rally · Speaker Series · Policy Briefing · Panel / Forum · Lecture · Conference / Summit · Webinar · Awards Gala · Gala · Fundraiser · Charity Festival · Networking · Registration Deadline · Remembrance Ceremony · Indigenous Ceremony · Ceremony · Community Meeting · Community Festival

## Jurisdictions

Kelowna · West Kelowna · Westbank First Nation · Peachland · Summerland · Central Okanagan (RDCO) · SD23 Central Okanagan · Provincial (BC) · Federal · Online

## Tags

- **Access:** Open to Public · Free · Ticketed · Registration Required · Members / Invite Only · Livestreamed · Delegations / Public Input
- **Who you'll meet:** Mayor & Council · MP · MLA · RDCO Directors · School Trustees · WFN Chief & Council · Business Leaders · Senior Public Servants · Party Members · Media
- **Topics:** Housing & Development · Land Use & Zoning · Budget & Taxes · Public Safety · Trade & Economy · Health Care · Education · Agriculture · Accessibility · Reconciliation · Veterans · Environment & Wildfire · Transportation · Tourism · Children & Youth
- **Priority:** GR Must-Attend · Networking Opportunity · Deadline
- **Status:** Details TBC
