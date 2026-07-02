# Tango Boise Website

Static website for **Tango Boise Inc.**, a 501(c)3 nonprofit tango dance organization. Content is aimed at a local dance community: class/practica info, event calendar, membership, and health & safety policies.

- Live at https://www.tangoboise.com, hosted on **GitHub Pages**
- Plain static site — no build step, no framework, no bundler
- Pages: `index.html`, `beginners.html`, `calendar.html`, `membership.html`, `health-safety.html`, `about.html`, `the-dance.html`
- Styles in `css/style.css`, interactivity in `js/main.js`
- Photos live in `images/`; the home page gallery auto-populates from that folder (files named `logo-*` are excluded — reserved for branding)
- "Upcoming events" blocks in `index.html`/`calendar.html` are auto-generated from Google Calendar by `scripts/sync_content.py` (run via a daily GitHub Actions workflow). Content between `<!-- SYNC:...:BEGIN -->` / `:END -->` comments should not be hand-edited — it will be overwritten on next sync.

See `README.md` for deployment/hosting details and `DEVELOPMENT.md` for local dev server setup and the content-editing guide.
