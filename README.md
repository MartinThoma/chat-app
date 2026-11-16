# P2P Chat

A messenger in a single HTML file that needs no server. People connect by swapping a short code once, then chat directly from browser to browser over an encrypted WebRTC connection. Chats are saved only in each person's own browser.

Use it at **https://martin-thoma.com/chat-app/**, or run it yourself:

- Open `index.html` in a browser (double-click works), or
- run `make run` to serve it on your network over HTTPS. It prints the URLs and your local IP. Set the port with `make run PORT=9000`.

`make run` uses a self-signed certificate, created on first run in `.cert/` with `openssl`. Browsers show a warning once; choose "Advanced" → "Proceed". HTTPS is required because the app uses the browser's cryptography, which browsers only allow on `https://` and `localhost`.

## Features

- No sign-up: your account is a key pair created in your browser on first use. A short onboarding screen explains the app and offers a password-protected backup.
- Everything you send is signed, so nobody can pretend to be you or change your messages. A security number lets two people verify each other.
- Back up your account to a file and restore it on another device.
- Personal chats and group chats. Group members don't all need to be connected to each other: members pass messages on.
- Messages written while someone isn't connected are sent when they reconnect, with a "Not delivered yet" marker until then.
- Delete a message for yourself, or your own message for everyone. Delete a chat, or leave a group.
- Name, contacts and history survive closing the browser.
- Light and dark mode, works on phones.
- Updates itself when a new version is published.

See [PRODUCT.md](PRODUCT.md) for the full feature description and its limits, [DESIGN.md](DESIGN.md) for the look and feel, and [ROADMAP.md](ROADMAP.md) for what's planned.

## How to connect

1. **Alice** clicks **Connect → Create invite** and sends the code to Bob (by messenger, email, SMS, …).
2. **Bob** clicks **Connect → Join with invite**, pastes the code, clicks **Accept invite** and sends back the reply code he gets.
3. **Alice** pastes the reply code and clicks **Connect**. Their personal chat opens.

Browsers can't connect to a bare IP address, so the codes carry each side's IP addresses, ports and encryption fingerprint. If connecting on the same network fails, open **Network settings** and enter your LAN IP (`make run` shows it).

Connections end on a reload, when the tab is closed, or when an IP address changes. Reconnect by swapping new codes. Your chats are kept.

## Releasing a new version

The version shown next to the title is `APP_VERSION` in `index.html`. It must match `version.json`. Change both with:

```sh
make bump VERSION=1.2.0
```

Then commit and push to `main`. GitHub Pages serves the repository root (Settings → Pages → Deploy from branch `main`, folder `/`).

Open copies of the app check `version.json` on load, every 5 minutes and whenever the tab becomes visible again. They always bypass the cache for this check.

- **Idle** (no connections, no dialog open): the app reloads itself with the new version right away.
- **Connected:** reloading would end the connections, so the app shows a banner with a **Reload now** button instead.
- **Mismatch:** if `version.json` and `index.html` disagree, the app reloads at most once and then only shows the banner.
