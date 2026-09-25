# iPhone Duo Playbook

A practical guide to bringing an existing iPhone app to iPhone Duo, Apple's first folding iPhone. Written for iOS developers and the coding agents they work with.

It combines Apple's documentation and the six iPhone Duo Tech Talks with field notes from shipping a real SwiftUI app to the Duo: where the fold actually is, the layouts that held up in every pose, the dead ends, and how to test poses on the simulator.

**[Read the playbook](PLAYBOOK.md)**

> **Get the update by email.** This version is written against the iOS 27.1 beta and the Duo simulator. I'll update it after testing on a real device at launch and again when iOS 27.1 ships. [Join the newsletter](https://newsletter.aivarsmeijers.com) to get the changes.

## What's inside

- The device in numbers, including measured fold positions and the SDK gate
- Five rules and a phased checklist: current SDK, iOS 27.1 SDK, App Store
- An API quick reference for SwiftUI and UIKit
- Fold-aware SwiftUI patterns: two pages in landscape, focal element above the hinge, cards centred on one page, passing the fold into scroll views
- Pitfalls and dead ends, including what the outer display can't do
- Simulator testing: capturing each display, a screen catalog, recording live pose changes
- Screenshots and App Store featuring
- An audit script and a ready-made prompt for a coding agent

## Use it with a coding agent

**Claude Code:** install the skill.

```bash
git clone https://github.com/aivars/iphone-duo-playbook.git
cp -R iphone-duo-playbook/skills/iphone-duo ~/.claude/skills/
```

Then ask: "Get this app ready for iPhone Duo."

**Other agents:** point them at [PLAYBOOK.md](PLAYBOOK.md) and use the prompt in §11.

## Run the audit

```bash
./scripts/duo-audit.sh ~/Developer/YourApp
```

It counts screen-based layout, idiom and orientation checks, fixed sizes, text-only buttons, sheets and more. Signals, not verdicts: read each hit before changing it.

## Watch it being built

I'm migrating my own apps to iPhone Duo on live streams, with AI coding agents doing much of the work. [YouTube](https://www.youtube.com/@aivarsmeijers) · [Can the Simulator Replace an iPhone Duo for App Testing?](https://www.youtube.com/watch?v=O3cKeXe09F4)

## Corrections welcome

APIs and behaviour may change before and after launch. If something here is wrong or missing, open an issue or a pull request.

## License

[MIT](LICENSE). Apple's documentation, Tech Talks and Xcode's bundled agent skills belong to Apple; this repo links to them and does not copy them.

By [Aivars Meijers](https://aivarsmeijers.com), indie iOS developer.
