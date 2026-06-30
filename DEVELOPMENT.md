# Local Development

This is a plain static site — no build step, no dependencies to install. You just need a local HTTP server (opening `index.html` directly as a `file://` URL can cause the Google Calendar iframes to fail due to browser security rules).

## Quickest option — Python (built into macOS/Linux)

```bash
cd tango-website
python3 -m http.server 8000
```

Open http://localhost:8000 in your browser.

## With Node.js

If you have Node installed, `npx` works without any prior install:

```bash
cd tango-website
npx serve .
```

Or install `http-server` once globally:

```bash
npm install -g http-server
http-server . -p 8000
```

## VS Code — Live Server extension

1. Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension
2. Open the `tango-website` folder in VS Code
3. Right-click `index.html` → **Open with Live Server**

The page reloads automatically whenever you save a file.

## Editing content

| What to change | File to edit |
|---|---|
| Home page | `index.html` |
| Beginner FAQ questions/answers | `beginners.html` |
| Upcoming events list | `calendar.html` — find the `MAINTAINER NOTE` comment |
| Membership tiers or prices | `membership.html` |
| Health & safety policies | `health-safety.html` |
| Contact info / about text | `about.html` |
| Colors, fonts, spacing | `css/style.css` — CSS variables are at the top |
| Nav toggle / FAQ accordion / calendar tabs | `js/main.js` |
| Photos | Drop files into `images/`, then add `<img>` tags where needed |

## Adding a new photo to the gallery

1. Copy the image file into `images/`
2. In `index.html`, find the `gallery-grid` section and add:
   ```html
   <a href="images/your-photo.jpg" class="gallery-link">
     <img src="images/your-photo.jpg" alt="Description" loading="lazy">
   </a>
   ```

## Changing the hero background image

In `css/style.css`, find `.hero-bg` and update the filename:

```css
.hero-bg {
  background-image: url('../images/your-new-hero.jpg');
}
```

## Updating the Mailchimp newsletter link

Search all HTML files for `https://mailchimp.com` and replace with your actual Mailchimp hosted signup URL (find it in Mailchimp → Audience → Signup forms → Form builder → publish a hosted page).

## File structure

```
tango-website/
├── index.html          ← Home page
├── beginners.html      ← Beginner FAQ
├── calendar.html       ← Events + Google Calendar embeds
├── membership.html     ← Membership tiers
├── health-safety.html  ← Policies
├── about.html          ← Contact & about
├── css/style.css       ← All styles
├── js/main.js          ← Interactivity
├── images/             ← All photos (self-hosted)
├── README.md           ← GitHub Pages deployment instructions
└── DEVELOPMENT.md      ← This file
```
