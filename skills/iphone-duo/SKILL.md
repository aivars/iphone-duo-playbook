---
name: iphone-duo
description: Use when adapting an existing iOS app (SwiftUI or UIKit) for iPhone Duo, Apple's folding iPhone, or when fixing layouts that break at new sizes, in landscape, around the fold, or with vertical toolbars and tab bars on iOS 27.1. Covers the audit, the phased checklist, fold-aware SwiftUI patterns, pitfalls and simulator testing.
---

# iPhone Duo

Read `playbook.md` in this folder in full before changing any code. It is the source of truth; this file only sets the order of work.

1. Run `bash audit.sh <repo> --details` (next to this file), report the counts, and inspect the hits. They are audit signals, not automatic defects.
2. Check the selected SDK, deployment target and existing changes. Work applicable Phase 1 items (playbook §3) in small, reviewable changes with tests after each. Follow the user's authorization requirements for commits and external actions.
3. Use Phase 2's 27.0 APIs with the 27.0 SDK and its 27.1 APIs only with the 27.1 SDK or newer. `#available` guards older runtimes; it does not make a new symbol compile with an older SDK. Preserve deployment targets and fallbacks unless agreed otherwise.
4. Base layout on available space and reserved regions, not device-model, idiom or hinge-angle pose checks. Do not mechanically remove non-layout checks. Never hard-code §1 device measurements. Choose active-only or inactive-region layout deliberately, and keep coordinate-space and RTL policies consistent (§5).
5. Preserve state above changing layout branches. Visually inspect affected screens on both Duo displays, in each relevant pose, and on regular iPhones. Run §7's accessibility, RTL, keyboard, live-transition and real-navigation checks; a screen catalog alone is insufficient.
6. Report changes, checks passed, blocked or untested configurations, and remaining playbook gaps. Distinguish simulator evidence from hardware validation. Do not publish, release or reset installations containing needed data without authorization.
