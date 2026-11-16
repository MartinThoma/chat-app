# P2P Chat: product description

P2P Chat is a messenger that runs entirely in the browser and needs no server. People connect by swapping a short code once, then chat directly from browser to browser. The whole app is one HTML file. It runs from https://martin-thoma.com/chat-app/, from a local web server, or by opening the file from disk.

## Principles

- **No server in the chat path.** Messages go from browser to browser over WebRTC data channels, encrypted with DTLS. Nothing is uploaded or stored centrally.
- **Data stays on the device.** Name, contacts and chat history live in the browser's local storage, and nowhere else.
- **One file, no build step.** No libraries, no framework, no install. Anyone can read, host or fork it.
- **Honest about limits.** Without a server some things can't work, such as reaching someone whose browser is closed. The app says so instead of pretending.

## Features

### Connecting to someone

Browsers can't open a connection to a bare IP address. Two people instead swap a **connection code**: an invite and a reply. The codes contain each side's IP addresses, ports and encryption fingerprint, compressed into one copyable string.

1. Alice clicks **Connect → Create invite** and sends the invite code to Bob by any channel: messenger, email, SMS.
2. Bob clicks **Connect → Join with invite**, pastes it, clicks **Accept invite** and sends back the reply code he gets.
3. Alice pastes the reply code and clicks **Connect**. The personal chat between them opens on both sides.

Each code works only once. Mistakes give clear errors, for example "That's an invite code, not a reply code".

### Identity and contacts

- Each browser creates a random, permanent user ID on first start. Everyone who connects is recognized by it, so reconnecting with new codes later continues the same chat.
- **Your name** sits in the top bar and can be changed at any time. Connected people see the change right away. Others see it when they next connect, together with a note in the chat ("Bob is now called Robert.").
- Everyone you've connected to becomes a **contact**. You can add contacts to groups even while they're not connected.

### Personal chats

- There's one chat per person. It appears in the chat list as soon as you connect for the first time.
- A green dot on the avatar shows that the person is connected right now.
- If they're not connected, the chat header says so and offers **Reconnect**. You can keep writing. Messages are sent when you're connected again.

### Group chats

- **New group** asks for a name (optional) and lets you pick members from your contacts.
- Any member can **add people** from their own contacts.
- Members don't all need to be connected to each other. Every member passes group messages on to the other members they're connected to. If Alice is connected to Bob and Carol, Bob and Carol can chat in the group without ever swapping codes with each other.
- **Leave group** removes you from the group for everyone and deletes the chat from your browser.
- The group header lists the members and how many are connected right now.

### Message delivery

- Every message has a unique ID. Duplicates, for example from being passed on by several members, are ignored.
- The recipient's app confirms each message that arrives. Until the first confirmation, your message shows **"Not delivered yet"**.
- Unconfirmed messages are kept and sent again the next time the recipient connects. This also covers connections that die silently, such as a closed laptop or a dropped Wi-Fi connection.
- Messages that can't be delivered within 30 days are dropped.

### Deleting

- **Delete for me** works on any message. It removes the message from this browser only.
- **Delete for everyone** works on your own messages. The message becomes "This message was deleted." for everyone in the chat. If a recipient isn't connected, the deletion reaches them later, the same way messages do. If the message hadn't been delivered yet, it's simply never sent.
- **Delete chat** removes a personal chat and all its messages from this browser. The other person keeps their copy. If they write again, the chat reappears.
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
- `make run` starts a local server and prints your LAN IP.

## Limits and non-goals

- **No relay server (TURN).** If both people are behind strict NATs, as on some mobile or office networks, a direct connection may not be possible.
- **Connections don't survive** a reload, closing the tab, or a change of IP address (Wi-Fi ↔ mobile data, VPN on or off). Reconnecting means swapping new codes. Chats and unsent messages are kept.
- **Offline people can't be reached.** A message reaches someone only while both of you are online and connected, directly or through a group member.
- **No sync between devices.** Each browser is its own identity with its own history.
- **Group delivery is best effort.** Members who are offline get missed group messages only when they next connect directly to the sender. Messages passed on by other members are not stored for later.
- **Group members can't be removed** by others. People can only leave.
- **"Delete for everyone" is a request.** It works with this app, but nobody can prevent a recipient from having read, copied or screenshotted a message.
- **Trust within groups.** Connections are encrypted, but messages are not signed, so a group member who passes messages on could change them or fake their sender. Groups are meant for people who trust each other.
- **Local storage is not encrypted.** Anyone with access to the browser profile can read the history.
- **Not included:** files and images, voice and video, reactions, editing, read receipts, typing indicators, push notifications.

## Protocol (for developers)

All packets are JSON sent over a single WebRTC data channel per connection.

| Packet | Fields | Purpose |
|---|---|---|
| `hello` | `id`, `name`, `v` | Sent first on every connection: user ID, name, app version |
| `msg` | `pid`, `id`, `from`, `name`, `text`, `ts`, `group?` | A chat message. `group` set means a group message, otherwise a personal message. |
| `del` | `pid`, `id`, `from`, `group?` | Delete for everyone. Only honored if `from` wrote message `id`. |
| `group` | `pid`, `group`, `gname`, `from`, `members[{id,name}]` | Create a group or add members |
| `leave` | `pid`, `group`, `from` | A member left |
| `ack` | `pid` | Confirms receipt. The sender removes the packet from its outbox. |

Group packets (`group` set) are passed on to connected members, with duplicates dropped by `pid`. Personal packets are accepted only directly from their author.
