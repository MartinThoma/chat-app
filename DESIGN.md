# P2P Chat: design

P2P Chat should feel like a familiar messenger: calm, quick to understand, nothing to learn. The unusual part, connecting by swapping codes, gets clear step-by-step guidance. Everything else follows conventions people know from WhatsApp, Signal or iMessage.

## Principles

- **Familiar over novel.** Chat list on the left, conversation on the right, my messages on the right in the accent color.
- **Quiet chrome, loud content.** Grays and white surfaces. Color is reserved for the accent (actions, my messages), status (connected, errors) and avatars.
- **Say what will happen.** Buttons name their result ("Accept invite", "Leave and delete"). Hints explain the consequence ("They keep their copy").
- **No motion.** Nothing animates. State changes appear instantly, which suits a tool that's often used for quick check-ins.
- **One file.** Only system fonts, no icon fonts, no images. Avatars are initials on colored backgrounds.

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
| `--shadow` | soft, 8% | soft, 35% | Onboarding card |

Text meets WCAG AA contrast (4.5:1) against its background in both themes.

**Avatars** get a hue computed from the user or group ID: `hsl(hue 45% 42%)` with white initials. The same person always has the same color, and the color works in both themes.

## Typography

- **Font:** `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`, so the app looks native on every platform. Connection codes use `ui-monospace`.
- **Scale:** three sizes in the app, each step at least 1.33× the previous one, with the largest exactly twice the smallest. A fourth, display size is used only for the onboarding headline on wide screens.

| Size | Used for |
|---|---|
| 48px / 600 | Onboarding headline (desktop only; 24px on phones), line height 1.08 |
| 24px / 600 | App title, welcome heading, onboarding step titles, security number |
| 16px / 400 and 600 | Body, messages, buttons, inputs, chat names, chat and dialog titles |
| 12px | Hints, timestamps, previews, message details, system lines, badges, connection codes |

- Line height is 1.45. Inputs are 16px so that iOS doesn't zoom in when one is tapped.
- Emphasis is by weight (600), never by an extra size.

## Layout

```
┌──────────────────────────────────────────────────────────┐
│ P2P Chat v1.2.0                       Your name [Alice]  │  top bar
├────────────────────┬─────────────────────────────────────┤
│ [Connect] [New grp]│ Trip                [Add] [Leave]   │  chat header
│ ● Trip      13:46  │ You, Bob · 1 connected              │
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
- **Sidebar footer:** the collapsible sections **Account** (backup, restore, account ID) and **Network settings** sit below the chat list.

### Onboarding screen

```
┌──────────────────────────────────────────────────────────┐
│ P2P Chat                                                 │
│                                  ┌────────────────────┐  │
│ Chat directly.                   │ Step 1 of 2        │  │
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
- **The setup card** is a panel with a 14px radius, a soft shadow and 28px padding. It has a small "Step 1 of 2" label, a 24px title, a muted explanation, and full-width buttons with one primary action. "Skip for now" and "Back" are text links, so they don't compete with it.
- **The "Backup saved" confirmation** uses a green check circle next to the title.

## Shape and spacing

| Element | Corner radius |
|---|---|
| Buttons, inputs, code boxes | 8px |
| Chat list rows, connection steps | 10px |
| Group avatars | 12px (rounded square, so groups and people look different) |
| Message bubbles, dialogs, onboarding card | 14px |
| People's avatars, online dot, badges | round |

Spacing steps are 4, 6, 8, 10, 12 and 16px. Gaps between related controls are 8px.

## Components

**Buttons.** Three kinds:
- Primary: accent fill, white text. One per view, for the main action.
- Secondary: panel fill with a border.
- Danger: red fill, only inside confirmation dialogs.

Disabled buttons are shown at 50% opacity.

**Chat list row.** Avatar (40px) with a green online dot for connected people. Name in 16px bold, last activity time on the right (12px muted, a time for today, otherwise a date). One line of preview below ("You: …", "Bob: …", "Message deleted"). An unread count badge sits on the right. The open chat has the `--selected` background.

**Message bubble.** The details line (12px, 85% opacity) holds sender, time and "Not delivered yet" while pending. A **Delete** link sits on the right of that line. It appears on hover or focus, and is always visible on touch screens. Deleted messages keep their bubble and read "This message was deleted." in italics.

**System lines.** Centered 12px muted text for events such as "Alice added you to the group." Day headings ("Today", "Mon, Nov 16, 2026") are the same, set in bold.

**Dialogs.** Native `<dialog>` elements, at most 460px wide, 14px radius, dimmed backdrop. Used for connecting, creating a group, adding people, and every confirmation. The title is 16px bold, followed by a muted explanation, with actions right-aligned. Escape and Cancel always close a dialog without side effects.

**Connection steps.** Numbered cards ("1. Send this invite code to your friend") with a monospace code box and a **Copy code** button that briefly changes to "Copied ✓".

**Update banner.** A full-width accent strip under the top bar: "Version x is available…" with **Reload now**.

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
- Buttons that only show an icon (✕, ←, Delete on a message) have an `aria-label`.
- Contrast is WCAG AA in light and dark mode.
