# Roadmap

Planned improvements. The order is the suggested order of work.

## A. Connect through mutual contacts

**Goal:** no code exchange between people who share a contact who is online.

WebRTC needs an offer and an answer to travel between two browsers before they can connect. Today, people carry them by hand as the invite and reply codes. Contacts who are already connected can carry them instead:

- If Alice and Bob are both connected to Carol, Alice's app sends its offer to Carol, addressed to Bob. Carol passes it on, and Bob's answer travels back the same way. Alice and Bob are then connected directly, and Carol is no longer involved.
- This makes **automatic reconnection** possible. After a reload, a network change or a new IP address, the app reconnects to every contact it can reach through someone who is online.
- Offers and answers are signed by their author, like all packets since 1.2. Carol can't change them or connect Alice to someone else. Carol does learn that Alice and Bob are connecting, and their IP addresses.

**Fits the principles:** no server is added.
**Limit:** it needs at least one existing connection. It doesn't help with the very first contact, or when nobody mutual is online.

## B. Optional public meeting points (done in 1.5)

**Goal:** one code (or link) is enough. Bob opens Alice's link and the connection forms by itself.

Shipped in 1.5 with Nostr relays: invite links and automatic reconnection between contacts. See "Meeting points" in [PRODUCT.md](PRODUCT.md).

- Use existing public infrastructure as a meeting point, for example Nostr relays or BitTorrent WebSocket trackers. The Trystero library uses this approach.
- Both browsers look for each other at the meeting point under a random topic derived from the invite. They exchange offer and answer there, encrypted with a key from the invite, then connect directly. Messages never pass through the meeting point.
- It also enables automatic reconnection when no mutual contact is online.
- **Opt-in**, off by default. The setting must say plainly what the relays see: which IP addresses meet, and when. They never see message content.

**Conflicts with the "no server" principle**, though these would be third-party servers, not ours. That's why it's optional.

## C. QR codes for meeting in person

**Goal:** connect without copying and pasting, when two people are in the same room.

- Show the invite and reply codes as QR codes, and scan them with the camera: Alice shows, Bob scans, Bob shows, Alice scans.
- Generate the QR code and scan it inside the page, keeping the app a single file.
- Works best with **shorter codes**. Today's codes are about 600–900 characters. Packing only the needed parts (fingerprint, password, addresses) as raw bytes would bring them down to roughly 100–180 characters. That's worth doing first, because it also makes pasting into messengers easier.

## D. Group calls

**Goal:** call a whole group.

- Every participant connects to every other participant, as in 1:1 calls. That works for small groups (about 4–6 people), because each browser sends its video to everyone.
- Needs direct connections between all participants, so it depends on A: members who haven't swapped codes would connect through the group automatically.
