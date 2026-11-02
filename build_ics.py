#!/usr/bin/env python3
"""Build calendar.ics from events.json for Outlook subscription.
Usage: python3 build_ics.py events.json calendar.ics
"""
import json, sys, datetime as dt
from zoneinfo import ZoneInfo

TZ = "America/Vancouver"
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

def main(src, dst):
    events = json.load(open(src))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Amar Khaira//Okanagan Political Events//EN",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         "X-WR-CALNAME:Okanagan Political & Civic Events",
         "X-WR-CALDESC:Political\\, civic\\, charity and community events in Okanagan Lake West—South Kelowna (Dan Albas) and Kelowna. Updated weekly.",
         "X-WR-TIMEZONE:" + TZ, "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"]
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
        L.append("SUMMARY:" + esc(f"[{e['cat']}] {e['title']}"))
        desc = f"Category: {e['cat']}\n\n{e['desc']}"
        if e.get("url"):
            desc += f"\n\nSource / more info: {e['url']}"
        L.append("DESCRIPTION:" + esc(desc))
        L.append("LOCATION:" + esc(e["location"]))
        L.append("CATEGORIES:" + esc(e["cat"]))
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
