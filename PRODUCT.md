# P2P Chat: product description

P2P Chat is a messenger that runs entirely in the browser and needs no server. People connect by swapping a short code once, then chat directly from browser to browser. The whole app is one HTML file. It runs from https://martin-thoma.com/chat-app/, from a local web server, or by opening the file from disk.

## Principles

- **No server in the chat path.** Messages go from browser to browser over WebRTC data channels, encrypted with DTLS. Nothing is uploaded or stored centrally.
- **Data stays on the device.** Name, contacts and chat history live in the browser's local storage, and nowhere else.
- **An account is a key pair.** No email, phone number or password. Your identity is a cryptographic key created in your browser, and everything you send is signed with it.
- **One file, no build step.** No libraries, no framework, no install. Anyone can read, host or fork it.
- **Honest about limits.** Without a server some things can't work, such as reaching someone whose browser is closed. The app says so instead of pretending.

## Features

### Onboarding

The first visit shows a welcome screen instead of the app:

- **Left side:** what the app is ("Chat directly. No server. No sign-up.") and how it works in three steps: your account lives on this device, you connect by swapping a code, you chat while you're both online.
- **Right side:** the account setup.
  1. **Create your account:** enter a name, then **Create account**. The key pair is created at this moment.
  2. **Back up your account:** set a password and **Download backup**, or **Skip for now**. A confirmation screen follows, then **Start chatting**.
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

- Every personal chat has **Verify**. It shows a 30-digit security number computed from both account IDs, so both people see the same number.
- Comparing it in person or on a call proves that nobody tampered with the codes you swapped. **They match, mark as verified** marks the contact as "Verified ✓".
- If a new contact connects with the same name as an existing one, the chat shows a note. That person may have created a new account, and "Verify" settles it.

### Connecting to someone

Browsers can't open a connection to a bare IP address. Two people instead swap a **connection code**: an invite and a reply. The codes contain each side's IP addresses, ports and encryption fingerprint, compressed into one copyable string.

1. Alice clicks **Connect → Create invite** and sends the invite code to Bob by any channel: messenger, email, SMS.
2. Bob clicks **Connect → Join with invite**, pastes it, clicks **Accept invite** and sends back the reply code he gets.
3. Alice pastes the reply code and clicks **Connect**. The personal chat between them opens on both sides.

Each code works only once. Mistakes give clear errors, for example "That's an invite code, not a reply code".

### Contacts

- Everyone you've connected to becomes a **contact**, recognized by their account ID. Reconnecting later with new codes continues the same chat.
- **Your name** sits in the top bar and can be changed at any time. Connected people see the change right away. Others see it when they next connect, together with a note in the chat ("Bob is now called Robert.").
- You can add contacts to groups even while they're not connected.

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
- `make run` starts a local HTTPS server with a self-signed certificate and prints your LAN IP. Browsers warn about the certificate once.

## Limits and non-goals

- **No relay server (TURN).** If both people are behind strict NATs, as on some mobile or office networks, a direct connection may not be possible.
- **Connections don't survive** a reload, closing the tab, or a change of IP address (Wi-Fi ↔ mobile data, VPN on or off). Reconnecting means swapping new codes. Chats and unsent messages are kept.
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
- **Not included:** files and images, voice and video, reactions, editing, read receipts, typing indicators, push notifications.

## Protocol (for developers)

All packets are JSON sent over a single WebRTC data channel per connection. The protocol version is `proto: 2`. Peers with another version are refused, with the message "uses a different version".

| Packet | Fields | Purpose |
|---|---|---|
| `hello` | `proto`, `v`, `id`, `pub`, `name`, `sig` | Sent first on every connection. `sig` signs `p2pchat-hello\n<own fingerprint>\n<other's fingerprint>`, using the DTLS fingerprints of this connection. `id` must equal the hash of `pub`. |
| `msg` | `pid`, `id`, `from`, `name`, `text`, `ts`, `group?`, `sig` | A chat message. `group` set means a group message, otherwise a personal message. |
| `del` | `pid`, `id`, `from`, `group?`, `sig` | Delete for everyone. Only honored if `from` wrote message `id`. |
| `group` | `pid`, `group`, `gname`, `from`, `members[{id,name,pub}]`, `sig` | Create a group or add members. Only accepted from an existing member. |
| `leave` | `pid`, `group`, `from`, `sig` | A member left |
| `ack` | `pid` | Confirms receipt. The sender removes the packet from its outbox. Not signed, because it only travels over the connection the identity was proven on. |

- **Signatures:** ECDSA P-256 with SHA-256, over `p2pchat-packet\n` followed by the packet without `sig`, serialized as JSON with sorted keys and no `undefined` fields. Keys and signatures are base64url.
- **Passing on:** group packets (`group` set) are passed on to connected members, and duplicates are dropped by `pid`. Personal packets are accepted only directly from their author.
- **Security number:** the SHA-256 hash of `p2pchat-safety\n<id1>\n<id2>`, with the IDs sorted. The first 24 bytes are read as six 32-bit numbers, each taken modulo 100000.
