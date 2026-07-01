#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["icalendar>=6.0", "recurring-ical-events>=3.0"]
# ///
"""
Regenerates the auto-generated regions of index.html / calendar.html:

- Upcoming events, pulled from the Tango Boise Google Calendars (public ICS feeds).
- The photo gallery, pulled from whatever image files are sitting in images/.

Maintainers don't touch this file's output by hand — edit the calendar or
drop a photo in images/, then let the GitHub Actions workflow (or a manual
`uv run scripts/sync_content.py`) regenerate the marked blocks below:

    <!-- SYNC:NAME:BEGIN --> ... <!-- SYNC:NAME:END -->

in index.html and calendar.html.
"""

import html
import re
import urllib.request
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import recurring_ical_events
from icalendar import Calendar

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Denver")
WINDOW_DAYS = 270
FESTIVAL_MIN_DAYS = 2

# The three "local" Boise calendars embedded as the "Boise Events" tab on
# calendar.html. The regional calendar is intentionally excluded here — it's
# a wider feed of other groups' events and isn't "our" upcoming events list.
CALENDAR_IDS = [
    "pfbbqtbco5rbbnhf6jduco2e6s@group.calendar.google.com",  # Solid Tango Events
    "3nviu676bq2f4geseldtq3g54s@group.calendar.google.com",  # Tango Boise Special Events
    "tfuqp4n6orervemcmcsl9v8n5g@group.calendar.google.com",  # Tango in Boise
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

CANCELLED_RE = re.compile(r"^\s*cancell?ed\b", re.IGNORECASE)
PREFIX_RE = re.compile(r"^[A-Z]{2,}:\s*")


class Event:
    def __init__(self, summary, start, end, all_day, location, recurring_freq):
        self.summary = summary
        self.start = start
        self.end = end
        self.all_day = all_day
        self.location = location
        self.recurring_freq = recurring_freq

    @property
    def duration_days(self):
        if self.all_day:
            return (self.end.date() - self.start.date()).days
        return (self.end - self.start).total_seconds() / 86400

    @property
    def clean_title(self):
        return html.escape(PREFIX_RE.sub("", self.summary).strip())

    @property
    def dedupe_key(self):
        if self.recurring_freq:
            return (self.clean_title, self.recurring_freq)
        return (self.clean_title, self.start.date())


def to_aware_datetime(value, end_of_day=False):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=TZ)
        return value.astimezone(TZ)
    if isinstance(value, date):
        t = time(23, 59, 59) if end_of_day else time(0, 0, 0)
        return datetime.combine(value, t, tzinfo=TZ)
    raise TypeError(f"Unexpected date value: {value!r}")


def fetch_calendar(calendar_id):
    url = f"https://calendar.google.com/calendar/ical/{calendar_id.replace('@', '%40')}/public/basic.ics"
    with urllib.request.urlopen(url, timeout=20) as resp:
        return Calendar.from_ical(resp.read())


def fetch_events():
    now = datetime.now(tz=TZ)
    window_end = now + timedelta(days=WINDOW_DAYS)

    events = []
    for calendar_id in CALENDAR_IDS:
        cal = fetch_calendar(calendar_id)
        occurrences = recurring_ical_events.of(cal).between(now, window_end)
        for vevent in occurrences:
            summary = str(vevent.get("SUMMARY", "")).strip()
            status = str(vevent.get("STATUS", "")).strip()
            if status.upper() == "CANCELLED" or CANCELLED_RE.match(summary):
                continue
            if not summary:
                continue

            raw_start = vevent["DTSTART"].dt
            raw_end = vevent["DTEND"].dt if vevent.get("DTEND") else raw_start
            all_day = not isinstance(raw_start, datetime)

            rrule = vevent.get("RRULE")
            freq = None
            if rrule and rrule.get("FREQ"):
                freq = str(rrule.get("FREQ")[0])

            events.append(
                Event(
                    summary=summary,
                    start=to_aware_datetime(raw_start),
                    end=to_aware_datetime(raw_end, end_of_day=all_day),
                    all_day=all_day,
                    location=str(vevent.get("LOCATION", "")).strip(),
                    recurring_freq=freq,
                )
            )

    events.sort(key=lambda e: e.start)

    deduped = {}
    for ev in events:
        key = ev.dedupe_key
        if key not in deduped or ev.start < deduped[key].start:
            deduped[key] = ev
    return sorted(deduped.values(), key=lambda e: e.start)


def classify_tag(event):
    s = event.summary.lower()
    if "milonga" in s:
        return "Milonga"
    if "practica" in s:
        return "Practica"
    if "festival" in s or "tree city" in s:
        return "Festival"
    if "clinic" in s or "workshop" in s:
        return "Workshop"
    if "class" in s or "lesson" in s:
        return "Class"
    return "Event"


def date_block(event):
    """Returns (month_label, day_label) for the small date badge."""
    if event.recurring_freq == "WEEKLY":
        return "Every", event.start.strftime("%a")
    if event.recurring_freq == "MONTHLY":
        return "Monthly", event.start.strftime("%a")
    return event.start.strftime("%b"), event.start.strftime("%-d")


def time_range_text(event):
    if event.all_day:
        return "All day"
    return f"{event.start.strftime('%-I:%M %p')} – {event.end.strftime('%-I:%M %p')}"


def venue_name(event):
    """Calendar locations are full street addresses; keep just the venue name."""
    if not event.location:
        return ""
    return html.escape(event.location.split(",")[0].strip())


def pick_featured(events):
    """First upcoming multi-day event (a festival), pulled out of the regular list."""
    for ev in events:
        if ev.duration_days >= FESTIVAL_MIN_DAYS:
            return ev
    return None


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------


def render_home_events(festival, events, limit=3):
    parts = []
    if festival:
        date_text = festival.start.strftime("%B %-d")
        if festival.end.date() != festival.start.date():
            date_text += f"–{festival.end.strftime('%-d, %Y')}"
        else:
            date_text += festival.start.strftime(", %Y")
        parts.append(f"""    <div class="featured-event">
      <div>
        <div class="featured-label">Annual Festival · Boise, Idaho</div>
        <h2>{festival.clean_title}</h2>
        <p class="event-date-text">{date_text}</p>
        <a href="calendar.html" class="btn btn-outline">View on Calendar</a>
      </div>
      <div class="featured-deco" aria-hidden="true">Tango</div>
    </div>
""")

    cards = []
    for ev in events[:limit]:
        month_label, day_label = date_block(ev)
        cards.append(f"""      <div class="event-card">
        <div class="event-date-block">
          <div class="month">{month_label}</div>
          <div class="day">{day_label}</div>
        </div>
        <div class="event-info">
          <span class="event-tag">{classify_tag(ev)}</span>
          <h3>{ev.clean_title}</h3>
          <div class="event-meta">
            <span>{time_range_text(ev)}</span>
            <span>{venue_name(ev) or "See calendar for venue"}</span>
          </div>
        </div>
      </div>""")

    parts.append("    <div class=\"events-grid\">\n" + "\n\n".join(cards) + "\n    </div>")
    return "\n".join(parts)


def render_featured_block(festival):
    if not festival:
        return ""
    date_text = festival.start.strftime("%B %-d")
    if festival.end.date() != festival.start.date():
        date_text += f"–{festival.end.strftime('%-d, %Y')}"
    else:
        date_text += festival.start.strftime(", %Y")
    return f"""    <div class="featured-event" style="margin-bottom:3.5rem;">
      <div>
        <div class="featured-label">Annual Festival · Boise, Idaho</div>
        <h2>{festival.clean_title}</h2>
        <p class="event-date-text">{date_text}</p>
        <p style="color:rgba(245,240,232,0.7);max-width:480px;margin-bottom:1.5rem;font-size:0.95rem;">
          Tango Boise's annual festival brings together dancers from across the region for workshops, milongas, and connection. See the calendar for full details.
        </p>
        <a href="about.html" class="btn btn-outline">Contact Us for Details</a>
      </div>
      <div class="featured-deco" aria-hidden="true">{festival.start.year}</div>
    </div>"""


def render_calendar_events(events, limit=8):
    items = []
    for ev in events[:limit]:
        month_label, day_label = date_block(ev)
        venue = venue_name(ev)
        location_text = f" &nbsp;·&nbsp; {venue}" if venue else ""
        items.append(f"""      <div class="upcoming-item">
        <div class="event-date-block">
          <div class="month">{month_label}</div>
          <div class="day">{day_label}</div>
        </div>
        <div class="event-info">
          <span class="event-tag">{classify_tag(ev)}</span>
          <h3>{ev.clean_title}</h3>
          <div class="event-meta">
            <span>{time_range_text(ev)}{location_text}</span>
          </div>
        </div>
      </div>""")
    return "\n\n".join(items)


def humanize_filename(filename):
    stem = Path(filename).stem
    stem = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", stem)
    stem = re.sub(r"[_\-]+", " ", stem)
    stem = re.sub(r"\b\d+\b", "", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return html.escape(stem.title()) if stem else "Tango Boise"


def render_gallery():
    images_dir = ROOT / "images"
    files = sorted(
        p.name
        for p in images_dir.iterdir()
        if p.suffix.lower() in IMAGE_EXTS and not p.name.lower().startswith("logo")
    )
    links = []
    for name in files:
        alt = humanize_filename(name)
        links.append(
            f'      <a href="images/{name}" class="gallery-link">'
            f'<img src="images/{name}" alt="{alt}" loading="lazy"></a>'
        )
    return "\n".join(links)


# ---------------------------------------------------------------------------
# File patching
# ---------------------------------------------------------------------------


def replace_block(text, marker, inner_html):
    begin = f"<!-- SYNC:{marker}:BEGIN -->"
    end = f"<!-- SYNC:{marker}:END -->"
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"Markers for {marker} not found")
    replacement = f"{begin}\n{inner_html}\n    {end}"
    return pattern.sub(lambda _m: replacement, text, count=1)


def main():
    events = fetch_events()
    festival = pick_featured(events)
    if festival:
        # Drop any other multi-day event landing on the same start date too —
        # the same festival is often entered separately in more than one calendar.
        remaining = [
            e for e in events
            if not (e.duration_days >= FESTIVAL_MIN_DAYS and e.start.date() == festival.start.date())
        ]
    else:
        remaining = events

    index_path = ROOT / "index.html"
    calendar_path = ROOT / "calendar.html"

    index_html = index_path.read_text()
    index_html = replace_block(index_html, "HOME-EVENTS", render_home_events(festival, remaining))
    index_html = replace_block(index_html, "GALLERY", render_gallery())
    index_path.write_text(index_html)

    calendar_html = calendar_path.read_text()
    calendar_html = replace_block(calendar_html, "FEATURED", render_featured_block(festival))
    calendar_html = replace_block(calendar_html, "EVENTS", render_calendar_events(remaining))
    calendar_path.write_text(calendar_html)

    print(f"Synced {len(events)} events ({'with' if festival else 'without'} a featured festival).")


if __name__ == "__main__":
    main()
