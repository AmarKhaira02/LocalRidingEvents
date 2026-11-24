#!/usr/bin/env python3
"""Build calendar.ics from events.json for Outlook subscription.
Usage: python3 build_ics.py events.json calendar.ics

Each event in events.json:
  required: id, cat, title, start, end (or allday), location, desc, url
  tagging:  type, jurisdiction, riding (optional), tags (list)
  detail (all optional, include whatever is known):
            organizer, attendees, cost, access, registration, livestream,
            contact, agenda, unconfirmed, gr_note
Unknown categories, types, jurisdictions or tags stop the build so the
tag vocabulary stays consistent.
"""
import json, sys, datetime as dt
from zoneinfo import ZoneInfo

TZ = "America/Vancouver"

CATEGORIES = [
    "Municipal Government", "Regional Government", "Committees & Advisory Bodies",
    "Federal & Provincial Politics", "Business & Economic Policy", "Charity & Fundraisers",
    "Community & NGO", "Indigenous & First Nations", "Ceremonies & Commemorations",
    "Education & Public Lectures",
]

# House of Commons-inspired colour per category: (CSS3 colour name for the
# RFC 7986 COLOR property, matching Outlook preset category colour).
# Greens = the Commons chamber, Dark Red = the Senate, gold = the Mace and
# crests, stone and wood = Centre Block.
CAT_COLORS = {
    "Federal & Provincial Politics": ("darkgreen", "Dark Green"),
    "Municipal Government": ("seagreen", "Green"),
    "Regional Government": ("teal", "Dark Teal"),
    "Committees & Advisory Bodies": ("olivedrab", "Olive"),
    "Education & Public Lectures": ("darkolivegreen", "Dark Olive"),
    "Business & Economic Policy": ("darkgoldenrod", "Dark Yellow"),
    "Charity & Fundraisers": ("darkred", "Dark Red"),
    "Indigenous & First Nations": ("sienna", "Dark Orange"),
    "Community & NGO": ("burlywood", "Dark Peach"),
    "Ceremonies & Commemorations": ("darkslategray", "Dark Steel"),
}
CAL_COLOR = "darkgreen"  # House of Commons green

# Specific event type: shown in the title prefix, e.g. "[Public Hearing · Kelowna]"
TYPES = [
    "Council Meeting", "Public Hearing", "Inaugural Meeting", "Committee of the Whole",
    "Budget Meeting", "Board Meeting", "Advisory Committee", "Town Hall",
    "Party Event", "Nomination Meeting", "AGM", "Candidate Forum", "Open House",
    "Public Consultation", "Protest / Rally", "Speaker Series", "Policy Briefing",
    "Panel / Forum", "Lecture", "Conference / Summit", "Webinar", "Awards Gala",
    "Gala", "Fundraiser", "Charity Festival", "Networking", "Registration Deadline",
    "Remembrance Ceremony", "Indigenous Ceremony", "Ceremony", "Community Meeting",
    "Community Festival",
]

JURISDICTIONS = [
    "Kelowna", "West Kelowna", "Westbank First Nation", "Peachland", "Summerland",
    "Central Okanagan (RDCO)", "Okanagan-Similkameen (RDOS)", "SD23 Central Okanagan",
    "SD67 Okanagan Skaha", "Provincial (BC)", "Federal",
    "Online",
]

RIDINGS = ["Okanagan Lake West—South Kelowna", "Kelowna"]

TAG_GROUPS = {
    "Access": ["Open to Public", "Free", "Ticketed", "Registration Required",
               "Members / Invite Only", "Livestreamed", "Delegations / Public Input"],
    "Who you'll meet": ["Mayor & Council", "MP", "MLA", "RDCO Directors", "School Trustees",
                        "WFN Chief & Council", "Business Leaders", "Senior Public Servants",
                        "Party Members", "Media"],
    "Topics": ["Housing & Development", "Land Use & Zoning", "Budget & Taxes", "Public Safety",
               "Trade & Economy", "Health Care", "Education", "Agriculture", "Accessibility",
               "Reconciliation", "Veterans", "Environment & Wildfire", "Transportation",
               "Tourism", "Children & Youth"],
    "Priority": ["GR Must-Attend", "Networking Opportunity", "Deadline"],
    "Status": ["Details TBC"],
}
TAGS = [t for group in TAG_GROUPS.values() for t in group]

DETAIL_FIELDS = [  # (json key, label)
    ("organizer", "Organizer"),
    ("attendees", "Who attends"),
    ("cost", "Cost"),
    ("access", "Access"),
    ("registration", "Registration / tickets"),
    ("livestream", "Livestream"),
    ("agenda", "Agenda"),
    ("contact", "Contact"),
]

VTZ = """BEGIN:VTIMEZONE
TZID:America/Vancouver
BEGIN:DAYLIGHT
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
TZNAME:PST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, b = [], line.encode("utf-8")
    while len(b) > 75:
        cut = 75 if not out else 74
        while (b[cut] & 0xC0) == 0x80:  # don't split UTF-8 chars
            cut -= 1
        out.append(b[:cut].decode()); b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)


def fmt_time(t):
    h = t.hour % 12 or 12
    ampm = "a.m." if t.hour < 12 else "p.m."
    return f"{h}:{t.minute:02d} {ampm}"


def when_text(e):
    if e.get("allday"):
        d = dt.date.fromisoformat(e["start"])
        return f"{d:%A, %B} {d.day}, {d.year} (all day / time TBC)"
    s = dt.datetime.fromisoformat(e["start"]); en = dt.datetime.fromisoformat(e["end"])
    txt = f"{s:%A, %B} {s.day}, {s.year}, {fmt_time(s)} to {fmt_time(en)}"
    if en.date() != s.date():
        txt = f"{s:%A, %B} {s.day}, {fmt_time(s)} to {en:%A, %B} {en.day}, {fmt_time(en)}"
    return txt + " (Kelowna time)"


def validate(e):
    errs = []
    if e["cat"] not in CATEGORIES:
        errs.append(f"unknown cat '{e['cat']}'")
    if e.get("type") and e["type"] not in TYPES:
        errs.append(f"unknown type '{e['type']}'")
    if e.get("jurisdiction") and e["jurisdiction"] not in JURISDICTIONS:
        errs.append(f"unknown jurisdiction '{e['jurisdiction']}'")
    if e.get("riding") and e["riding"] not in RIDINGS:
        errs.append(f"unknown riding '{e['riding']}'")
    for t in e.get("tags", []):
        if t not in TAGS:
            errs.append(f"unknown tag '{t}'")
    return [f"{e['id']}: {x}" for x in errs]


def summary(e):
    bits = [x for x in (e.get("type"), e.get("jurisdiction")) if x]
    prefix = " · ".join(bits) if bits else e["cat"]
    return f"[{prefix}] {e['title']}"


def description(e):
    out = [f"WHEN: {when_text(e)}", f"WHERE: {e['location']}"]
    out.append("")
    out.append(f"CATEGORY: {e['cat']}")
    if e.get("type"):
        out.append(f"TYPE: {e['type']}")
    if e.get("jurisdiction"):
        out.append(f"JURISDICTION: {e['jurisdiction']}")
    if e.get("riding"):
        out.append(f"FEDERAL RIDING: {e['riding']}")
    if e.get("tags"):
        out.append("TAGS: " + ", ".join(e["tags"]))
    out.append("")
    out.append("ABOUT:")
    out.append(e["desc"])
    if e.get("gr_note"):
        out += ["", "WHY IT MATTERS (GOVERNMENT RELATIONS):", e["gr_note"]]
    details = [f"{label}: {e[k]}" for k, label in DETAIL_FIELDS if e.get(k)]
    if details:
        out += ["", "DETAILS:"] + details
    if e.get("unconfirmed"):
        out += ["", "NOT YET CONFIRMED: " + e["unconfirmed"]]
    if e.get("url"):
        out += ["", f"SOURCE: {e['url']}"]
    return "\n".join(out)


def main(src, dst):
    events = json.load(open(src))
    errors = [x for e in events for x in validate(e)]
    if errors:
        sys.exit("Tag/category errors:\n  " + "\n  ".join(errors))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Amar Khaira//Okanagan Political Events//EN",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         "X-WR-CALNAME:Okanagan Political & Civic Events",
         "X-WR-CALDESC:Political\\, civic\\, charity and community events in Okanagan Lake West—South Kelowna (Dan Albas) and Kelowna. Updated daily.",
         "COLOR:" + CAL_COLOR, "X-APPLE-CALENDAR-COLOR:#006400",
         "X-WR-TIMEZONE:" + TZ, "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H"]
    # Times are emitted in UTC (converted with current tzdata, which includes
    # BC's permanent UTC-7 from Nov 2026) so Outlook shows correct local times.
    for e in sorted(events, key=lambda x: x["start"]):
        L.append("BEGIN:VEVENT")
        L.append(f"UID:{e['id']}@okanagan-political-cal")
        L.append(f"DTSTAMP:{now}")
        if e.get("allday"):
            d = dt.date.fromisoformat(e["start"])
            L.append(f"DTSTART;VALUE=DATE:{d:%Y%m%d}")
            L.append(f"DTEND;VALUE=DATE:{d + dt.timedelta(days=1):%Y%m%d}")
        else:
            z = ZoneInfo(TZ); u = dt.timezone.utc
            s = dt.datetime.fromisoformat(e["start"]).replace(tzinfo=z).astimezone(u)
            en = dt.datetime.fromisoformat(e["end"]).replace(tzinfo=z).astimezone(u)
            L.append(f"DTSTART:{s:%Y%m%dT%H%M%SZ}")
            L.append(f"DTEND:{en:%Y%m%dT%H%M%SZ}")
        L.append("SUMMARY:" + esc(summary(e)))
        L.append("DESCRIPTION:" + esc(description(e)))
        L.append("LOCATION:" + esc(e["location"]))
        cats = [e["cat"]] + [x for x in (e.get("type"), e.get("jurisdiction")) if x] + e.get("tags", [])
        L.append("CATEGORIES:" + ",".join(esc(c) for c in dict.fromkeys(cats)))
        L.append("COLOR:" + CAT_COLORS[e["cat"]][0])
        if e.get("url"):
            L.append("URL:" + e["url"])
        L.append("TRANSP:TRANSPARENT")  # don't block your free/busy
        L.append("END:VEVENT")
    L.append("END:VCALENDAR")
    with open(dst, "w", newline="") as f:
        f.write("\r\n".join(fold(l) for l in L) + "\r\n")
    print(f"Wrote {len(events)} events to {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
