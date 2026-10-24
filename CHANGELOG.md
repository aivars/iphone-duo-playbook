# Changelog

## 1.6 (2026-10-24)

- Refresh the release status for Xcode 27.1 final and accepted 27.2 RC builds; distinguish current requirements from April 2027 SDK and Duo screenshot gates.
- Correct ArrangementView navigation nesting; replace the blanket orientation-lock claim with scoped testing guidance.
- Add an active-fold helper and use it for the seated portrait example, avoiding a needless split when flat while preserving deliberate two-page layouts.
- Add Release artifact/provenance checks, conditional production gates, and explicit uploaded/submitted/approved/released reporting.
- Capture release lessons: RTL and background-test false positives, semantic tab selectors, subscription-sheet dismissal, isolated screenshot fixtures and upload receipts.
- Label screenshot-set uploads deprecated but historically working; outline the App Asset Library migration without claiming an untested CLI workflow is verified.
- Add screenshot majority-in-use guidance, extreme-size iPhone Mirroring checks and Apple's documented agent-skill export command. Preserve simulator/hardware and historical-toolchain limits.

## 1.5.1 (2026-10-22)

- §1/§5.1 correction: on the 27.1 RC an **inactive** division keeps its band's full thickness; only `isActive` distinguishes flat from folded. The earlier "zero width when flat" note matched a beta. Found when a flat-open layout kept splitting around the hinge.

## 1.5 (2026-10-20)

Pose scripting, from adapting a second app (a fasting timer).

- §7: RocketSim's `duo pose closed|book|open` sets simulator poses headlessly — the first scriptable alternative to Device Hub; its coordinate taps mistranslate on a posed Duo, so target elements semantically (AXPress).
- §7: Device Hub itself cannot be scripted: it exposes no windows or menus to the accessibility API (Xcode 27.1 RC).

## 1.4 (2026-10-14)

Field notes from shipping an iPhone Duo App Store release.

- Status: Xcode 27.1 RC builds are accepted for App Store submission; App Store Connect now accepts iPhone Duo screenshots and previews.
- §3 Phase 3: Duo screenshot set and preview sizes (1920 × 886 / 886 × 1920); added the iOS 27 product page header as a release decision.
- §7: capturing without scripting the pose (reuse a posed simulator, static screens before timed ones, auto-detect undrawn frames, back up app containers).
- §8: screenshot design notes (show every pose early, landscape framing, demo-data copy, half-empty book-pose screens) and the App Store Connect API upload path for `APP_IPHONE_DUO`.
- §8: new section on product page header and search results assets: Apple's specs, template safe areas, what iPhone shows in practice, text and art advice.
- §9: links to Apple's creative assets specifications and asset best practices.

## 1.3.1 (2026-09-28)

- §8 featuring nomination timing clarified: Apple's lead time (at least 2 weeks' notice, 3 weeks recommended, ideally up to 3 months) counts back from your own publish date, not the iPhone Duo launch. There is no Duo-specific nomination deadline; iOS 27.1 SDK updates can't publish before iOS 27.1 ships.

## 1.3 (2026-09-26)

Readability pass; no facts, links or code changed.

- Added an "At a glance" section with the five steps that matter most.
- Split dense paragraphs into a bold lead plus short bullets (SDK gate notes, checklist items, Phase 2 build rules, §5 notes, pitfalls, reset, store, audit).
- Turned the coding-agent prompt into nine numbered steps; "How to use this" now points agents to it.

## 1.2 (2026-09-26)

- Separated compliant App Store screen-recording previews from filmed marketing demos, with the App Review rule linked.
- Replaced the padding-only scroll-coordinate recipe with viewport-first guidance and explicit conversion requirements for moving content.
- Replaced manual page offsets with semantic stacks matching mirrored reserved-region coordinates; documented RTL policy and bounded-viewport assumptions.
- Made inactive-region handling a deliberate layout choice, not a universal requirement.
- Reframed fixed sizes, safe-area arithmetic, grid counts and off-screen buttons as contextual audit signals rather than automatic defects.
- Distinguished SDK compile-time requirements from runtime availability; 27.0 improvements no longer require the 27.1 SDK.
- Added accessibility, keyboard, real-navigation and state-continuity acceptance checks; clarified beta-simulator versus hardware evidence and safe reset practices.
- Aligned the installable agent instructions, added audit line references and error handling, and removed the duplicated inline script from the playbook.
- Added repeatable audit tests and SDK type-checking of the playbook's Swift layout snippets. These checks do not establish runtime layout correctness.

## 1.1 (2026-09-26)

Fact-checked against Apple's current documentation, HIG, API reference, Tech Talks and the Group Lab Q&A.

- Every Apple claim and API now links to its Apple source; our own simulator findings are marked "field observation".
- Device numbers reframed: Apple publishes pixels only, so point sizes are labeled as derived and for testing only. Added the inner panel's physical resolution.
- SDK gate rewritten from Apple's Tech Talk: Xcode 26 builds keep an iPhone aspect ratio, Xcode 27.0 extends left of the status bar on the inner display, Xcode 27.1 is edge to edge with vertical bars. Phases now name exact Xcode and SDK versions instead of "current SDK". Added a release status box (Xcode 27.1 is beta; TestFlight only).
- Fixed: UIKit `preferredVerticalBarBehavior` must be overridden, not assigned.
- Fixed API availability: `presentationPlacement`, `visibilityPriority`, `ToolbarOverflowMenu`, `defaultTabBarPlacement` and `topBarPinnedTrailing` are iOS 27.0; `additionalOverflowItems` and `pinnedTrailingGroup` are iOS 16. Added an iOS column to the API table.
- Fixed: custom toolbar views can opt into vertical bars with `axisBehavior(.verticalPreferred)`; Device Hub shipped in Xcode 27 (only the Duo simulator needs 27.1); `AVCaptureDevice.RotationCoordinator` spelling; sidebar tabs need `.sidebarAdaptable`.
- Corrected: system sheets slide aside to avoid the fold (Apple); removed an unsourced claim about the standby clock; AlarmKit is the other outer-display case Apple mentions.
- Store: App Store Connect lists Duo screenshot and preview sizes but can't accept uploads yet. Featuring lead time: at least 3 weeks.
- Added from Apple: `UIScreen.main` deprecation, `UIRequiresFullScreen`, even grid columns, new windows only on the inner display, lost touches over the camera region, the direction coordinator, simulator known issues, Previews display override.
- US spelling throughout; full Tech Talk titles.

## 1.0 (2026-09-26)

First public version, written against the iOS 27.1 beta and the Device Hub simulator.

- Device numbers, measured fold positions, and the SDK gate (iOS 26 SDK: compatibility mode on a black background; 27.0: more of the display with blank space; 27.1: edge-to-edge with vertical bars).
- Five rules, phased checklist, API quick reference.
- Fold-aware SwiftUI patterns, pitfalls, simulator testing, store and featuring notes.
- Audit script and a Claude Code skill.
