# P2P Chat: product description

P2P Chat is a messenger that runs entirely in the browser and needs no server. People connect by swapping a short code once, then chat directly from browser to browser. The whole app is one HTML file, plus a few small files for notifications and installing. It runs from https://martin-thoma.com/chat-app/, from a local web server, or by opening the file from disk.

## Principles

- **No server in the chat path.** Messages go from browser to browser over WebRTC data channels, encrypted with DTLS. Nothing is uploaded or stored centrally.
- **Data stays on the device.** Name, contacts and chat history live in the browser's local storage, and nowhere else.
- **An account is a key pair.** No email, phone number or password. Your identity is a cryptographic key created in your browser, and everything you send is signed with it.
- **One file, no build step.** No libraries, no framework, nothing to set up. Anyone can read, host or fork it. Next to `index.html` there are only a service worker for notifications (`sw.js`) and what installing needs (`manifest.webmanifest` and `icons/`).
- **Honest about limits.** Without a server some things can't work, such as reaching someone whose browser is closed. The app says so instead of pretending.

## Features

### Onboarding

The first visit shows a welcome screen instead of the app:

- **Left side:** what the app is ("Chat directly. No server. No sign-up.") and how it works in three steps: your account lives on this device, you connect by swapping a code, you chat while you're both online.
- **Right side:** the account setup.
  1. **Create your account:** enter a name, then **Create account**. The key pair is created at this moment.
  2. **Back up your account:** set a password and **Download backup**, or **Skip for now**. A confirmation screen follows, then **Continue**.
  3. **Allow calls:** **Allow microphone and camera** makes the browser ask for access now, with an explanation, instead of in the middle of the first call. **Skip for now** is fine too. If access is refused, the step explains how to allow it in the site settings.
- **Restore from a backup** is offered on the first step, for people who already have an account.

On phones the order is intro, then setup, then how it works, so the setup form is visible without scrolling far.

### Account and identity

- On **Create account**, the browser creates an ECDSA P-256 key pair. Every current browser supports this algorithm.
- Your **account ID** is derived from the public key: the first 18 bytes of its SHA-256 hash. Nobody can use your ID without your private key.
- On every connection, both sides prove their identity. Each signs the certificate fingerprints of both ends of that exact encrypted connection. A captured proof is useless on any other connection.
- Every message, deletion, group change and "leave" is signed by its author. Recipients check the signature, including for group messages that other members passed on. A member who passes messages on can't change them or pretend to be someone else.
- The account lives in local storage: key, name, contacts and chats. Opening the app again skips onboarding.
- Browsers only allow this cryptography over `https://`, on `localhost`, and for files opened from disk. Opened over plain HTTP from another address, the app explains this instead of starting.

### Backup and restore

- **Back up account** creates one file, `p2pchat-backup-<name>-<date>.json`. It contains the private key, name, contacts, chats and messages waiting to be sent. You can make one during onboarding, or later under **Account** in the sidebar.
- The file is encrypted with AES-GCM. The key is derived from your password with PBKDF2-SHA-256, 600,000 iterations. Passwords need at least 8 characters, and nobody can recover a forgotten one.
- **Restore** is offered during onboarding and under **Account**. It asks for the file and password, checks that the private key matches the public key, then replaces the account and chats in this browser. A wrong password gives "Wrong password, or the file is damaged."
- Use the backup to move to another device, or to recover after clearing browser data.

### Verifying contacts

- Every personal chat has **Verify security number** in its chat details (⋮). It shows a 30-digit security number computed from both account IDs, so both people see the same number.
- Comparing it in person or on a call proves that nobody tampered with the codes you swapped. **They match, mark as verified** marks the contact as "Verified ✓".
- If a new contact connects with the same name as an existing one, the chat shows a note. That person may have created a new account, and verifying the security number settles it.

### Connecting to someone

Browsers can't open a connection to a bare IP address. Two people instead swap a **connection code**: an invite and a reply. The codes contain each side's IP addresses, ports and encryption fingerprint, compressed into one copyable string.

1. Alice clicks **Connect → Create invite** and sends the invite code to Bob by any channel: messenger, email, SMS.
2. Bob clicks **Connect → Join with invite**, pastes it, clicks **Accept invite** and sends back the reply code he gets.
3. Alice pastes the reply code and clicks **Connect**. The personal chat between them opens on both sides.

Each code works only once. Mistakes give clear errors, for example "That's an invite code, not a reply code".

### Meeting points (optional)

With **Use public meeting points** turned on (Network settings, or **Use a single link instead** in the Connect dialog), the codes travel through public Nostr relays instead of by hand:

- **Invite links.** **Connect → Create invite link** gives a link like `https://martin-thoma.com/chat-app/#join=…`. Send it to your friend; when they open it (or paste it into **Join with invite**), the two apps find each other and connect, as long as P2P Chat is open on both sides. A link works once and stays valid for 7 days, also after a reload. **Cancel this invite** and **Cancel open invite links** withdraw it.
- **Automatic reconnection.** Contacts who both use meeting points find each other again after a reload, a closed tab or a network change, usually within a few seconds. The chat header says "You reconnect automatically when Bob is online".
- **Consent.** It's off by default. Turning it on, and opening an invite link while it's off, first explains what the relays can see and asks.
- **What the relays see:** your IP address, when you're online, and a random topic that changes daily, so they could tell which IP addresses meet. They don't see names, account IDs or messages: offer and answer are encrypted with a key only the two people know, events are signed with a throwaway key per page load, and chats still go directly between you. The hello still proves who's on the other end.
- **Relays:** `nos.lol`, `relay.primal.net`, `nostr.mom` and `relay.nostr.net` by default, editable in Network settings (any Nostr relay that passes on ephemeral events works, including your own). The settings show how many are connected.
- A meeting point only replaces the code exchange. Connecting across the internet still needs STUN, as before.

### Contacts

- Everyone you've connected to becomes a **contact**, recognized by their account ID. Reconnecting later with new codes continues the same chat.
- **Your name** sits in the top bar and can be changed at any time. Connected people see the change right away. Others see it when they next connect, together with a note in the chat ("Bob is now called Robert.").
- You can add contacts to groups even while they're not connected.

### Personal chats

- There's one chat per person. It appears in the chat list as soon as you connect for the first time.
- A green dot on the avatar shows that the person is connected right now.
- The chat header shows the name and status, a phone icon (**Call**), a camera icon (**Video call**) and **⋮** for the chat details. The call icons are disabled, with the reason as a tooltip, while the person isn't connected or you're already in a call.
- **Chat details** (⋮): avatar, connection status, verified state and the start of the account ID, with **Reconnect** (while not connected), **Verify security number** (or **Show security number**) and **Delete chat**.
- If they're not connected, the chat header says so. You can keep writing. Messages are sent when you're connected again.

### Group chats

- **New group** asks for a name (optional) and lets you pick members from your contacts.
- Any member can **add people** from their own contacts.
- Members don't all need to be connected to each other. Every member passes group messages on to the other members they're connected to. If Alice is connected to Bob and Carol, Bob and Carol can chat in the group without ever swapping codes with each other.
- The group header has only **⋮**. Its chat details list the members (who's connected right now) and offer **Add people** and **Leave group**.
- **Leave group** removes you from the group for everyone and deletes the chat from your browser.
- The group header lists the members and how many are connected right now.

### Calls

- The phone and camera icons in the header of a personal chat start a call while the other person is connected. Calls use the existing connection, so no new codes are needed. Sound and video go directly between the two browsers, encrypted, like messages.
- The browser asks for microphone (and camera) access the first time, unless it was already allowed during onboarding or under **Set up calls**. The other person's phone only rings once that's granted.
- **Set up calls** (sidebar section **Calls**) shows whether the microphone and camera are allowed, blocked or not asked yet. It asks for access, lets you pick which microphone and camera to use (remembered for calls), and tests them with a live level bar and a camera preview. Both switch off when the window closes.
- **Blocked access:** browsers don't ask again once access was refused. The app then explains where to allow it (the site settings next to the address), and the error after a failed call offers **Set up calls**. An incoming call warns right away if the microphone is blocked.
- **Incoming call:** a full-screen view with the caller's name, a ring tone, and **Accept**, **Decline** and, for video calls, **Answer without video**. The tab title says who's calling. Unanswered calls stop ringing after 45 seconds.
- **During a call:** **Mute**, **Turn camera on/off** (also in a voice call), **Show chat** and **Hang up**. The other side sees when you're muted, and sees your avatar instead of video while your camera is off. Without a camera, a video call continues as a voice call.
- **Show chat** shrinks the call into a green bar above the app ("Call with Bob · 3:12", **Return to call**, **Hang up**), so you can keep writing.
- Every call leaves a note in the chat: "Video call, 3:12", "Bob declined the call.", "Bob didn't answer.", "Missed voice call from Alice." Missed calls count as unread.
- **One call at a time.** A second caller is told that you're on another call, and you get a missed-call note. If two people call each other at the same moment, the calls merge into one.
- A call ends when the connection drops (with a note). Closing the tab hangs up properly.

### Messages

- Each message shows its time at the bottom right: when you sent it, or, for messages from others, when it arrived on your device. In groups, other people's messages show their name on top.
- Your own messages show their status right of the time: **Not delivered** while waiting, **✓** delivered, **✓✓** read. In a group, ✓✓ means everyone has read it.
- A message counts as read when its chat is on screen: the tab is visible, the chat is open (on phones, the chat panel is showing) and no call screen covers it. Your app then sends a read receipt to the author. Receipts are delivered like messages, so they arrive later if the author isn't connected.
- **Selecting:** long-press a message (right-click on a computer, or Enter on a focused message) to select it. While something is selected, tapping other messages adds or removes them, and the chat header becomes a bar with **Copy**, **Details** (for one message) and **Delete**. ✕ or Escape ends the selection.
- **Details** shows when a message was sent, delivered and read. For a group message, it lists every member with "Read …", "Delivered …" or "Not delivered yet". For a received message: who sent it, when it was sent (by their clock), when it arrived and when you read it.
- Messages from before 1.6 have no arrival or read times, and contacts with an older version don't send read receipts.

### Notifications

- **Show notifications** (sidebar section **Notifications**, or **Also turn on notifications** at the end of onboarding) asks the browser for permission once.
- While P2P Chat is open but not in front (another tab, another window, minimized), new messages show a system notification with the sender (and the group) as title and the message as text. Each chat has one notification; a newer message replaces it, and opening the chat removes it.
- **Include message text** (on by default) can be turned off for privacy: the notification then only says "New message" or "3 new messages".
- Incoming calls show "Bob is calling you" until you answer, decline or the call ends; missed calls leave a "Missed voice call from Bob" notification.
- Tapping a notification brings P2P Chat to the front and opens the chat or the call.
- While the window isn't in front, messages also don't count as read, so no read receipt is sent until you come back.
- If the browser blocks notifications, the section says where to allow them (site settings, and on Android the Chrome app's notification setting).

### Installing as an app

- P2P Chat can be installed like an app: it then opens in its own window, without the browser's address bar, and has an icon on the home screen, in the app list or on the desktop. It's the same app at the same address, and it updates itself the same way.
- The sidebar section **Install app** explains it. In Chrome and Edge it has an **Install P2P Chat** button that opens the browser's own install confirmation. Other browsers only offer installing in their menu ("Install app", "Add to Home screen"), so the section says where to look. On iPhone and iPad it says: tap Share, then **Add to Home Screen**. In Safari on a Mac: File, then **Add to Dock**.
- In Chrome, Edge and on Android, the installed app shares its chats and account with the browser. On iPhone and iPad, and with Safari on a Mac, the installed app keeps its own storage, so it starts empty: move the account there with **Back up account** and **Restore from backup**. The section says so.
- The section is hidden while P2P Chat runs as an installed app, and when it's opened from disk (a file can't be installed).
- Installing changes nothing about connections: the app still has to be open to receive messages.

### Message delivery

- Every message has a unique ID. Duplicates, for example from being passed on by several members, are ignored.
- The recipient's app confirms each message that arrives. Until the first confirmation, your message shows **"Not delivered yet"**.
- Unconfirmed messages are kept and sent again the next time the recipient connects. This also covers connections that die silently, such as a closed laptop or a dropped Wi-Fi connection.
- Messages that can't be delivered within 30 days are dropped.

### Deleting

- Deleting starts from a selection (see Messages), so several messages can be deleted at once. **Delete for everyone** is offered when all selected messages are your own.
- **Delete for me** works on any message. It removes the message from this browser only.
- **Delete for everyone** works on your own messages. The message becomes "This message was deleted." for everyone in the chat. If a recipient isn't connected, the deletion reaches them later, the same way messages do. If the message hadn't been delivered yet, it's simply never sent.
- **Delete chat** (in the chat details) removes a personal chat and all its messages from this browser. The other person keeps their copy. If they write again, the chat reappears.
- **Leave group** works as described under group chats.
- Every deletion asks for confirmation. The safe choice ("Cancel") has keyboard focus.

### History and storage

- Chats, contacts, your name and messages waiting to be sent survive closing the tab, the browser or the computer.
- Each chat keeps its last 1,000 messages. If the browser's storage fills up, the oldest messages of the largest chat are dropped first.
- Messages are grouped by day, with date headings.
- Unread messages show a count on the chat and in the browser tab title, for example "(3) P2P Chat".

### One tab at a time

Only one tab can be connected and saving at a time. Opening the app in a second tab moves the connections there. The first tab shows "P2P Chat is open in another tab" with a **Use here** button.

### Updates

- The current version is shown next to the title, for example "v1.1.0", and links to the source code.
- The app checks `version.json` on start, every 5 minutes and when the tab becomes visible again. This check always bypasses the browser and CDN caches.
- When a new version is out and nothing is going on (no connections, no dialog open), the app reloads itself. Otherwise it shows a banner with **Reload now**. Chats are saved, so reloading only ends the live connections.

### Network settings

- **STUN server**, `stun:stun.l.google.com:19302` by default. It only tells your browser its public IP so people can connect across the internet. No messages pass through it. Leave it empty for local-network or fully offline use.
- **Your IP address**: browsers hide local IPs behind random `….local` names, which some networks can't resolve. If connecting on the same network fails, entering your LAN IP puts it into your codes instead.
- **Use public meeting points**, with the list of relays (see Meeting points). Off by default.
- `make run` starts a local HTTPS server with a self-signed certificate and prints your LAN IP. Browsers warn about the certificate once.

## Limits and non-goals

- **No relay server (TURN).** If both people are behind strict NATs, as on some mobile or office networks, a direct connection may not be possible.
- **Connections don't survive** a reload, closing the tab, or a change of IP address (Wi-Fi ↔ mobile data, VPN on or off). Without meeting points, reconnecting means swapping new codes. With meeting points on both sides, the apps reconnect by themselves. Chats and unsent messages are kept either way.
- **Meeting points need both apps open at the same time.** Relays pass messages on without storing them, so an invite link only connects while the inviter's app is open too.
- **Automatic reconnection needs one connection made with 1.5 or later**, because that's when the two apps agree on their shared meeting secret.
- **Offline people can't be reached.** A message reaches someone only while both of you are online and connected, directly or through a group member.
- **No sync between devices.** Each browser is its own identity with its own history.
- **Group delivery is best effort.** Members who are offline get missed group messages only when they next connect directly to the sender. Messages passed on by other members are not stored for later.
- **Group members can't be removed** by others. People can only leave.
- **"Delete for everyone" is a request.** It works with this app, but nobody can prevent a recipient from having read, copied or screenshotted a message.
- **Group members can read what they pass on.** Messages are encrypted per connection, not end to end per message. Every member can read group messages, which is intended, and a member who passes messages on could also hold them back.
- **The first code exchange is trusted.** If someone tampered with the codes on their way, only comparing security numbers ("Verify") reveals it.
- **Local storage is not encrypted.** Anyone with access to the browser profile can read the history and use the account key.
- **Losing the key means a new account.** Without a backup, clearing browser data creates a new identity, and contacts see you as a new person.
- **One device at a time.** A restored backup is the same account. Using it on two devices at once works, but each device keeps its own history.
- **No upgrade path from 1.1.** Version 1.2 introduced key-based accounts. Chats from 1.1 stay in the browser's storage, but the app doesn't show them, and 1.1 and 1.2 can't connect to each other.
- **Calls are one-to-one.** There are no group calls yet, and nobody can join a running call.
- **Calls need both people connected right now.** There's no ringing someone who isn't connected, and no voicemail.
- **No notifications while the app is closed.** A closed tab runs no code and has no connections, so messages can't even arrive. Phones also pause background tabs after a few minutes. Push notifications would need the browser maker's push service and probably a small relay; see roadmap item E.
- **Not included:** files and images, reactions, editing, typing indicators, push notifications while the app is closed.

## Protocol (for developers)

All packets are JSON sent over a single WebRTC data channel per connection. The protocol version is `proto: 2`. Peers with another version are refused, with the message "uses a different version".

| Packet | Fields | Purpose |
|---|---|---|
| `hello` | `proto`, `v`, `caps`, `id`, `pub`, `name`, `sig` | Sent first on every connection. `sig` signs `p2pchat-hello\n<own fingerprint>\n<other's fingerprint>`, using the DTLS fingerprints of this connection. `id` must equal the hash of `pub`. `caps` lists optional features, currently `["call"]` (since 1.3). |
| `msg` | `pid`, `id`, `from`, `name`, `text`, `ts`, `group?`, `sig` | A chat message. `group` set means a group message, otherwise a personal message. |
| `del` | `pid`, `id`, `from`, `group?`, `sig` | Delete for everyone. Only honored if `from` wrote message `id`. |
| `group` | `pid`, `group`, `gname`, `from`, `members[{id,name,pub}]`, `sig` | Create a group or add members. Only accepted from an existing member. |
| `leave` | `pid`, `group`, `from`, `sig` | A member left |
| `call` | `a`, `call`, `video?`, `mic?`, `cam?` | Call control, never stored or acknowledged. `a` is `ring` (with `video`), `accept`, `decline`, `busy`, `end`, or `state` (with `mic` and `cam`, sent when they change). `call` is a random call ID. |
| `rtc` | `desc` or `cand` | Adds or removes microphone and camera on the existing connection: an SDP offer or answer, or an ICE candidate. Collisions are resolved by "perfect negotiation": the side with the smaller account ID gives way. |
| `rv` | `rv` | The meeting secret for this pair of contacts (32 random bytes, base64url). Sent by the side with the smaller account ID after every hello. |
| `read` | `pid`, `from`, `to`, `ids[]`, `at`, `group?`, `sig` | Read receipt for up to 100 messages by `to`, read at `at` (reader's clock). Group receipts are only passed on to `to`. |
| `ack` | `pid` | Confirms receipt. The sender removes the packet from its outbox. Not signed, because it only travels over the connection the identity was proven on. |

- **Signatures:** ECDSA P-256 with SHA-256, over `p2pchat-packet\n` followed by the packet without `sig`, serialized as JSON with sorted keys and no `undefined` fields. Keys and signatures are base64url.
- **Unsigned packets:** `ack`, `call`, `rtc` and `rv` aren't signed. They're only accepted on a connection whose `hello` was verified, so they can only come from that person.
- **Passing on:** group packets (`group` set) are passed on to connected members, and duplicates are dropped by `pid`. Personal packets are accepted only directly from their author.
- **Security number:** the SHA-256 hash of `p2pchat-safety\n<id1>\n<id2>`, with the IDs sorted. The first 24 bytes are read as six 32-bit numbers, each taken modulo 100000.

### Meeting points

Nostr events of kind `25050` (ephemeral: relays pass them on without storing them), tagged `["t", topic]`, signed with BIP-340 Schnorr by a random key per page load.

- **Secret:** 16 random bytes for an invite link (in the URL fragment, which browsers never send to a web server), or the pair's `rv`.
- **Topic:** hex SHA-256 of `p2pchat-meet-topic\n<day>\n<secret>`, where `<day>` is days since 1970 (UTC). Apps listen on yesterday's, today's and tomorrow's topic and publish on today's.
- **Content:** base64url of a 12-byte IV followed by AES-256-GCM ciphertext, with the key SHA-256 of `p2pchat-meet-key\n<secret>`. The plaintext is JSON: `{type, from, ts, to?, oid?, code?}`. `from` is a random ID for the page; `code` is a normal connection code.
- **Invite link:** the joiner sends `offer` every 6 seconds (with a new offer every 60 seconds); the inviter replies `answer` with the same `oid`. The link is used up when the hello succeeds.
- **Contacts:** both sides send `here` when they come online, when the network comes back, when a connection drops and every 5 minutes. The side with the smaller account ID answers a `here` with an `offer`; the other side answers `here` with `here`, and an `offer` with an `answer`. The hello must come from the expected contact.
- Messages older than 10 minutes, not addressed to this page, or that fail to decrypt are ignored.
