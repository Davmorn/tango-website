# Tango Boise Website

Static website for [Tango Boise Inc.](https://www.tangoboise.com) — a 501(c)3 nonprofit.  
Hosted on GitHub Pages. No build step required.

## Hosting on GitHub Pages

1. Push this repo to GitHub (e.g. `github.com/Davmorn/tango-website`)
2. Go to **Settings → Pages**
3. Set **Source** to `main` branch, `/ (root)` folder
4. Your site will be live at `https://davmorn.github.io/tango-website/`

To use a custom domain (e.g. `tangoboise.com`):
- Add a `CNAME` file in this folder containing just: `tangoboise.com`
- Update your DNS to point to GitHub Pages (see [GitHub docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site))

---

## Updating Content

### Upcoming events (home page + `calendar.html`)

These are auto-generated — don't hand-edit the blocks between `<!-- SYNC:...:BEGIN -->` and `<!-- SYNC:...:END -->` comments. To change what's listed, edit the Google Calendars themselves (the same ones embedded on `calendar.html`); a GitHub Actions workflow re-syncs the site daily, and on every push that touches `images/`. To resync immediately, run it manually from the Actions tab ("Sync events & gallery" → Run workflow) or locally with `uv run scripts/sync_content.py`. See `scripts/sync_content.py` for how events are picked (the three local calendars, next ~9 months, with any multi-day event treated as the featured festival).

### Photo gallery

Drop an image file into `images/` (commit + push) and the gallery on the home page picks it up automatically on the next sync — no HTML editing needed. Files named `logo-*` are skipped.

### Adding your Google Calendar embed

1. Open [Google Calendar](https://calendar.google.com) → Settings → click your calendar name → **"Integrate calendar"**
2. Copy the **Embed code** (an `<iframe>` tag)
3. In `calendar.html`, find the `HOW TO ADD YOUR GOOGLE CALENDAR` comment block and replace it with your iframe
4. Do the same for the Regional Calendar section below it
5. If you change which calendars are embedded, also update `CALENDAR_IDS` in `scripts/sync_content.py` so the auto-synced events list matches

### Updating the Mailchimp newsletter link

Search for `https://mailchimp.com` in `index.html` and `calendar.html` and replace with your actual Mailchimp signup URL.

### Updating contact info (`about.html`)

Replace `info@tangoboise.com` and any `TODO` comments with your actual contact details.

---

## File Structure

```
tango-website/
├── index.html          # Home / Welcome page
├── beginners.html      # Beginner's FAQ
├── calendar.html       # Events + Google Calendar embed
├── membership.html     # Membership tiers & signup
├── health-safety.html  # Health & Safety & Conduct policies
├── about.html          # About & Contact
├── css/
│   └── style.css       # All styles (dark tango theme)
├── js/
│   └── main.js         # Nav toggle, FAQ accordion, calendar tabs
├── images/             # Drop your photos here — gallery auto-updates
├── scripts/
│   └── sync_content.py # Pulls events from Google Calendar, rebuilds the gallery
└── .github/workflows/
    └── sync-content.yml # Runs sync_content.py daily + on image pushes
```

## Adding Photos

Place image files in the `images/` folder — the gallery section on the home page picks them up automatically (see "Photo gallery" above). To add a hero background image, add this to `style.css` inside `.hero`:

```css
.hero {
  background-image: url('images/your-photo.jpg');
}
```

Then adjust the `.hero::before` overlay opacity to taste.
