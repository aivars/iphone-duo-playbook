# iPhone Duo Playbook

A practical guide to bringing an existing iPhone app to iPhone Duo, Apple's first folding iPhone. Written for iOS developers and the coding agents they work with.

It combines Apple's documentation, the six iPhone Duo Tech Talks and the Group Lab Q&A with field notes from adapting an existing, released SwiftUI app in the Duo beta simulator: measured fold positions, layout experiments, dead ends, and how to test transitions. Physical-device validation remains a separate step after launch.

**[Read the playbook](PLAYBOOK.md)**

> **Get the update by email.** This version is written against the iOS 27.1 beta and the Duo simulator. I'll update it after testing on a real device at launch and again when iOS 27.1 ships. [Join the newsletter](https://newsletter.aivarsmeijers.com) to get the changes.

## What's inside

- The device: size classes, orientation, the SDK gate (Xcode 26, 27.0, 27.1), and test sizes with their Apple sources
- Five rules and a phased checklist: current SDK, iOS 27.1 SDK, App Store
- An API quick reference for SwiftUI and UIKit
- Fold-aware SwiftUI patterns: two pages in landscape, focal element above the hinge, cards centered on one page, RTL and viewport/content coordinate handling
- Pitfalls and dead ends, including what the outer display can't do
- Simulator testing: capturing each display, a screen catalog, live transitions, accessibility, keyboard and state-continuity checks
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
./scripts/duo-audit.sh ~/Developer/YourApp --details
```

It counts regex matches for screen-based layout, idiom and orientation checks, fixed sizes, text-only buttons, sheets and more. `--details` adds file and line references. Signals, not verdicts: read each hit before changing it. This is not a Swift parser or a readiness certification.

## Maintaining this guide

After editing the playbook or audit script, run `bash scripts/sync-skill.sh` to update the installable copies. Run `python3 scripts/test-audit.py` and `python3 scripts/check-swift-examples.py` to validate the audit behavior and type-check the layout examples. The Swift check needs Xcode 27.1 or newer; it does not replace visual or hardware testing.

## Watch it being built

I'm migrating my own apps to iPhone Duo on live streams, with AI coding agents doing much of the work. [YouTube](https://www.youtube.com/@aivarsmeijers) · [Can the Simulator Replace an iPhone Duo for App Testing?](https://www.youtube.com/watch?v=O3cKeXe09F4)

## Corrections welcome

APIs and behaviour may change before and after launch. If something here is wrong or missing, open an issue or a pull request.

## License

[MIT](LICENSE). Apple's documentation, Tech Talks and Xcode's bundled agent skills belong to Apple; this repo links to them and does not copy them.

By [Aivars Meijers](https://aivarsmeijers.com), indie iOS developer.
