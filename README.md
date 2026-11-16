# P2P Chat

A chat app in a single HTML file that needs no server. Messages go directly from browser to browser over an encrypted WebRTC connection.

Use it at **https://martin-thoma.com/chat-app/**, or run it yourself:

- Open `index.html` in a browser (double-click works), or
- run `make run` to serve it on your network. It prints the URLs and your local IP. Set the port with `make run PORT=9000`.

## How to connect

Browsers can't open a connection to a bare IP address. Instead, the two people swap a short **connection code**. The code holds each side's IP addresses, ports and encryption fingerprint.

1. **Alice** clicks **Create invite** and sends the code to Bob (by messenger, email, SMS, …).
2. **Bob** clicks **Join with invite**, pastes the code and sends back the **reply code** he gets.
3. **Alice** pastes the reply code and clicks **Connect**. The chat opens.

For a group chat, one person creates a separate invite for each friend. Messages are forwarded between everyone who is connected.

## Network settings

- **STUN server** (default `stun:stun.l.google.com:19302`): only used to find out your public IP so you can connect across the internet. No messages pass through it. Leave it empty for LAN-only or fully offline use.
- **Your IP address** (optional): browsers hide your local IP behind a random `….local` name. If connecting on the same network fails, enter your LAN IP here and create a new code.

## Limits

- There is no relay (TURN) server. If both people are behind strict NATs (some mobile or corporate networks), a direct connection may not be possible.
- Codes work only once. Create new ones after a reload.
- Nothing is stored. Messages are gone when you close the tab.

## Releasing a new version

The version shown next to the title is `APP_VERSION` in `index.html`. It must match `version.json`. Change both with:

```sh
make bump VERSION=1.1.0
```

Then commit and push to `main`. GitHub Pages serves the repository root (Settings → Pages → Deploy from branch `main`, folder `/`).

Open copies of the app check `version.json` on load, every 5 minutes and whenever the tab becomes visible again. They always bypass the cache for this check.

- **Idle** (no open chats, no invite in progress): the app reloads itself with the new version right away.
- **During a chat:** reloading would end the chat, so the app shows a banner with a **Reload now** button instead.
- **Mismatch:** if `version.json` and `index.html` disagree, the app reloads at most once and then only shows the banner.
