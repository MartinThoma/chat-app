# P2P Chat: design

P2P Chat should feel like a familiar messenger: calm, quick to understand, nothing to learn. The unusual part, connecting by swapping codes, gets clear step-by-step guidance. Everything else follows conventions people know from WhatsApp, Signal or iMessage.

## Principles

- **Familiar over novel.** Chat list on the left, conversation on the right, my messages on the right in the accent color.
- **Quiet chrome, loud content.** Grays and white surfaces. Color is reserved for the accent (actions, my messages), status (connected, errors) and avatars.
- **Say what will happen.** Buttons name their result ("Accept invite", "Leave and delete"). Hints explain the consequence ("They keep their copy").
- **No motion.** Nothing animates. State changes appear instantly, which suits a tool that's often used for quick check-ins. The only moving things are live readings: video, and the microphone level bar in **Set up calls**.
- **One file.** Only system fonts, no icon fonts, no image files. The few icons (phone, camera, ⋮) are inline SVGs from Feather (MIT license), drawn with `currentColor` so they follow the theme. Avatars are initials on colored backgrounds. The extra files are `sw.js`, a tiny service worker that exists because Chrome on Android shows notifications only through one, and what installing as an app needs: `manifest.webmanifest` and the app icon in `icons/`.

## Color

All colors are CSS variables on `:root`. Dark mode follows the operating system through `prefers-color-scheme`.

| Token | Light | Dark | Used for |
|---|---|---|---|
| `--bg` | `#f5f6f8` | `#12151b` | Page and chat background, input fields |
| `--panel` | `#ffffff` | `#1b1f27` | Top bar, sidebar, chat header, composer, dialogs |
| `--text` | `#1d2330` | `#e4e7ee` | Body text |
| `--muted` | `#596173` | `#9aa2b3` | Hints, timestamps, previews, system lines |
| `--border` | `#dde1e8` | `#2c323e` | Dividers, input and button borders |
| `--accent` | `#2f6fed` | `#3d6fe0` | Primary buttons, unread badges, update banner |
| `--mine` / `--mine-text` | `#2f6fed` / white | `#3d6fe0` / white | My message bubbles |
| `--theirs` / `--theirs-text` | `#eceff4` / `#1d2330` | `#262b35` / `#e4e7ee` | Other people's bubbles |
| `--hover` | `#eef1f6` | `#222731` | Hovered list rows |
| `--selected` | `#e3e9f6` | `#29303d` | Open chat in the list |
| `--ok` | `#1f9d55` | `#3cbf74` | "Connected" dot |
| `--bad` | `#c93636` | `#f07a7a` | Error text |
| `--danger` | `#c93636` | `#c93636` | Destructive buttons (white text) |
| `--call` | `#137a42` | `#137a42` | Call bar, **Accept** button (white text) |
| `--shadow` | soft, 8% | soft, 35% | Onboarding card |

Text meets WCAG AA contrast (4.5:1) against its background in both themes.

The **call screen** is always dark (`#0e1116`, white text, secondary text `#c3c9d5`), in both themes, so video stands out and the screen doesn't glare in a dark room.

**Avatars** get a hue computed from the user or group ID: `hsl(hue 45% 42%)` with white initials. The same person always has the same color, and the color works in both themes.

**App icon.** Two speech bubbles in white on the accent blue `#2f6fed`: a solid one in front, a 55% translucent one behind it. `icons/icon.svg` has rounded corners (radius 112 of 512) and is also the favicon. `icons/icon-maskable.svg` fills the square and shrinks the bubbles to fit the safe zone, for Android's round and squircle masks and the iPhone home screen. The PNGs are rendered from these with `make icons`.

The installed app's title bar follows `--panel` (white, or `#1b1f27` in dark mode) through `theme-color`, so it continues the top bar. The launch screen uses `--bg` from the light theme.

## Typography

- **Font:** `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`, so the app looks native on every platform. Connection codes use `ui-monospace`.
- **Scale:** three sizes in the app, each step at least 1.33× the previous one, with the largest exactly twice the smallest. A fourth, display size is used only for the onboarding headline on wide screens.

| Size | Used for |
|---|---|
| 48px / 600 | Onboarding headline (desktop only; 24px on phones), line height 1.08. Initial in the large call avatar |
| 24px / 600 | App title, welcome heading, onboarding step titles, security number, caller's name |
| 16px / 400 and 600 | Body, messages, buttons, inputs, chat names, chat and dialog titles |
| 12px | Hints, timestamps, previews, message details, system lines, badges, connection codes |

- Line height is 1.45. Inputs are 16px so that iOS doesn't zoom in when one is tapped.
- Emphasis is by weight (600), never by an extra size.

## Layout

```
┌──────────────────────────────────────────────────────────┐
│ P2P Chat v1.2.0                       Your name [Alice]  │  top bar
├────────────────────┬─────────────────────────────────────┤
│ [Connect] [New grp]│ Bob                    ☎  ▭◁  ⋮    │  chat header
│ ● Trip      13:46  │ Connected                           │
│   Bob: see you!    ├─────────────────────────────────────┤
│ ● Bob       13:40  │            Today                    │
│ ● Carol     Nov 14 │ ┌────────────┐                      │
│                    │ │ Bob · 13:46│          ┌─────────┐ │
│                    │ │ see you!   │          │ You ·…  │ │
│                    │ └────────────┘          └─────────┘ │
│ ▸ Network settings ├─────────────────────────────────────┤
│                    │ [Message the group…        ] [Send] │  composer
└────────────────────┴─────────────────────────────────────┘
   sidebar 320px                 chat (fills the rest)
```

- **Desktop (wider than 760px):** a sidebar of fixed width 320px next to the chat. Only the chat list and the message list scroll.
- **Phone (760px and narrower):** one panel at a time. The chat list is the home screen. Opening a chat replaces it, and **←** goes back. Message bubbles may use 88% of the width instead of 75%.
- **Side spacing** is 16px everywhere (top bar, sidebar sections, chat header, messages, composer).
- **Sidebar footer:** the collapsible sections **Account** (backup, restore, account ID), **Calls** (access status, **Set up calls**), **Notifications** (two checkboxes and an explanation), **Install app** (an explanation and, where the browser allows it, **Install P2P Chat**; hidden inside the installed app) and **Network settings** sit below the chat list.

### Onboarding screen

```
┌──────────────────────────────────────────────────────────┐
│ P2P Chat                                                 │
│                                  ┌────────────────────┐  │
│ Chat directly.                   │ Step 1 of 3        │  │
│ No server.                       │ Create your account│  │
│ No sign-up.            (48px)    │ Your name [      ] │  │
│ Messages go straight from …      │ [ Create account ] │  │
│                                  │ ─────── or ─────── │  │
│ ① Your account lives on …        │ [Restore a backup] │  │
│ ② Connect by swapping a code …   └────────────────────┘  │
│ ③ Chat while you're both online …                        │
└──────────────────────────────────────────────────────────┘
```

- A full-screen page shown on the first visit, in place of the app. It's a two-column grid at most 1040px wide, vertically centered: on the left the intro and "how it works", on the right the setup card.
- **Phones (860px and narrower):** one column in the order intro, setup card, how it works, so the form appears early. The headline drops to 24px.
- **The headline** is set on three fixed lines. "sign-up" uses a non-breaking hyphen, so it never splits.
- **"How it works" items** are numbered with 32px circles (`--selected` fill), a bold title and muted text.
- **The setup card** is a panel with a 14px radius, a soft shadow and 28px padding. It has a small "Step 1 of 3" label, a 24px title, a muted explanation, and full-width buttons with one primary action. "Skip for now" and "Back" are text links, so they don't compete with it.
- **The "Backup saved" confirmation** uses a green check circle next to the title.

## Shape and spacing

| Element | Corner radius |
|---|---|
| Buttons, inputs, code boxes | 8px |
| Chat list rows, connection steps | 10px |
| Group avatars | 12px (rounded square, so groups and people look different) |
| Message bubbles, dialogs, onboarding card | 14px |
| Call buttons | pill (fully rounded) |
| People's avatars, online dot, badges | round |

Spacing steps are 4, 6, 8, 10, 12 and 16px. Gaps between related controls are 8px.

## Components

**Buttons.** Three kinds:
- Primary: accent fill, white text. One per view, for the main action.
- Secondary: panel fill with a border.
- Danger: red fill, only inside confirmation dialogs.

Disabled buttons are shown at 50% opacity.

**Chat list row.** Avatar (40px) with a green online dot for connected people. Name in 16px bold, last activity time on the right (12px muted, a time for today, otherwise a date). One line of preview below ("You: …", "Bob: …", "Message deleted"). An unread count badge sits on the right. The open chat has the `--selected` background.

**Chat header.** Name (16px bold) and status (12px muted) on the left. On the right, 40px round icon buttons without a border: phone and camera (personal chats only) and ⋮. Icons are 22px, in the text color; hover shows the `--hover` circle. Disabled call icons stay in place at 50% opacity, so the header never shifts.

**Chat details dialog.** Opened with ⋮. A centered 64px avatar (rounded square for groups) with the status below; for groups, the member list (28px avatars, "Connected" on the right). Then a column of full-width, left-aligned buttons: the normal actions first, the destructive one ("Delete chat", "Leave group") last in red text. Destructive actions still ask for confirmation.

**Message bubble.** Text first. The time (12px, 85% opacity) floats at the bottom right: beside a short last line, or on its own line below. My messages add the status right of the time: "· Not delivered", ✓ (delivered) or ✓✓ (read, set slightly bolder). Screen readers hear "You, 13:46, read". In groups, other people's bubbles start with the sender's name in 12px bold. Deleted messages keep their bubble and read "This message was deleted." in italics.

**Selection.** Long press (450ms, cancelled by moving more than 10px), right-click or Enter selects a bubble. Selected bubbles get a 3px accent outline with a 2px gap, so it also shows on my accent-colored bubbles. The chat header is replaced by the selection bar: ✕, "2 selected" (16px bold), and **Copy**, **Details**, **Delete** on the right. On touch screens, text in bubbles can't be selected by hand, so a long press never starts a text selection; **Copy** replaces that.

**Message details.** A regular dialog: the message as muted text in a tinted box (`--bg`, 8px radius), then a two-column list (muted labels such as "Sent", "Delivered", "Read", or member names in groups; full date and time with seconds), then a short muted note about whose clock a time comes from.

**System lines.** Centered 12px muted text for events such as "Alice added you to the group." Day headings ("Today", "Mon, Nov 16, 2026") are the same, set in bold.

**Dialogs.** Native `<dialog>` elements, at most 460px wide, 14px radius, dimmed backdrop. Used for connecting, creating a group, adding people, and every confirmation. The title is 16px bold, followed by a muted explanation, with actions right-aligned. Escape and Cancel always close a dialog without side effects.

**Connection steps.** Numbered cards ("1. Send this invite code to your friend") with a monospace code box and a **Copy code** button that briefly changes to "Copied ✓". Invite links use a two-line box with **Copy link** and, where the browser can share, **Share…**. Step 2 says what happens next and offers **Cancel this invite** as a text link. "Swap codes by hand instead" sits below as a small text link.

**Meeting points setting.** A checkbox with a bold 12px label in Network settings, followed by a muted explanation that changes with the state: what it's for while off; what the relays can see while on. Turning it on (also from the Connect dialog's "Use a single link instead", or by opening an invite link) always goes through a confirmation that spells out what the relays see. The relay list and status only appear while it's on. Open sidebar sections scroll inside at most 40% of the window height, so the chat list stays visible.

**Update banner.** A full-width accent strip under the top bar: "Version x is available…" with **Reload now**.

**Call screen.** A full-window dialog on the dark call background.
- Without video: the person's avatar (112px) centered, with their name (24px) and the status below: "Calling…", "Incoming video call…", or the running time ("3:12 · Bob is muted").
- With video: the other person's video fills the screen, letterboxed (`object-fit: contain`) so nothing is cropped. Avatar, name and time shrink into a dark translucent chip at the top left.
- Your own camera shows as a mirrored 176px preview at the bottom right (104px on phones). It's hidden while your camera is off.
- Buttons are text pills in one centered row at the bottom, wrapping on phones: translucent white for **Mute**, **Turn camera on/off** and **Show chat**; red for **Hang up** and **Decline**; green (`--call`) for **Accept**. **Mute** turns solid white while you're muted, so the state is visible at a glance.
- Escape goes back to the chat instead of hanging up.

**Set up calls dialog.** A regular dialog: a muted line about what's used and when (or, when blocked, where to allow it), then **Allow microphone and camera** as the primary button. Once allowed, it shows a microphone picker with a native `<meter>` level bar under it, a camera picker, and a mirrored 4:3 camera preview with an 8px radius.

**Call bar.** A full-width green strip (`--call`) under the top bar while a call runs in the background: "Call with Bob · 3:12" with **Return to call** and **Hang up**.

**Call notes.** Calls appear in the chat as system lines ("Video call, 3:12", "Missed voice call from Alice.").

**Full-page notices.** Centered 24px title with muted text, covering the whole page:
- "P2P Chat is open in another tab", with **Use here**.
- "Open P2P Chat over a secure connection", shown when the browser blocks cryptography, for example on plain HTTP from another device.

**Security number dialog.** Six groups of five digits in a 3×2 grid, set in a 24px semibold monospace font so they're easy to read aloud. Above them, a short explanation of how to compare. The primary button reads "They match, mark as verified". Verified contacts show "Verified ✓" in the chat header and on the button.

**Password fields.** Backups use two password fields ("Backup password", "Repeat password") with the browser's `new-password` autocomplete, so password managers offer to store them. Errors appear in red 12px text right above the button.

## Voice and copy

- Plain, short, second person: "Paste the reply code here", "Delete chat with Bob?"
- Explain consequences, especially for deleting: who keeps a copy, what happens if they write again.
- No technical terms outside **Network settings**. There we say "STUN server" and "IP address", because people who open that section need them.
- Status is stated, not implied: "Not connected. Your messages are sent when you reconnect."

## Accessibility

- Every control can be reached with the keyboard. Dialogs trap focus, because `showModal()` does that.
- Confirmation dialogs put focus on the safe choice.
- New incoming messages are announced through a hidden `aria-live="polite"` area ("Bob in Trip: see you!"). The message list itself is not a live region, because it's redrawn on every change and would otherwise be read out again in full.
- Buttons that only show an icon (✕, ←, phone, camera, ⋮) have an `aria-label`, and a `title` tooltip with the same text, or with the reason when disabled.
- Contrast is WCAG AA in light and dark mode.
