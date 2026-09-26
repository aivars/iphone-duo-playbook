# Changelog

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
