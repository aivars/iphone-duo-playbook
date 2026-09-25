---
name: iphone-duo
description: Use when adapting an existing iOS app (SwiftUI or UIKit) for iPhone Duo, Apple's folding iPhone, or when fixing layouts that break at new sizes, in landscape, around the fold, or with vertical toolbars and tab bars on iOS 27.1. Covers the audit, the phased checklist, fold-aware SwiftUI patterns, pitfalls and simulator testing.
---

# iPhone Duo

Read `playbook.md` in this folder in full before changing any code. It is the source of truth; this file only sets the order of work.

1. Run `audit.sh <repo>` (next to this file) and report the numbers.
2. Work Phase 1 of the checklist (playbook §3): one commit per checklist item, tests passing after each.
3. Start Phase 2 only if the project builds with the iOS 27.1 SDK. Gate 27.1 APIs with `#available`.
4. Never add device, idiom or pose checks (playbook §2, rules 1 and 4). For the fold, use the reserved-region patterns in §5.
5. After any layout change, capture the affected screens on the outer display, the inner display in portrait and in landscape, and a regular iPhone (§7). Look at the captures yourself before calling the change done.
6. Finish by listing anything the playbook got wrong or does not cover.
