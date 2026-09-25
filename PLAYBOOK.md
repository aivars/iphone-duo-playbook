# iPhone Duo Playbook

This is a practical guide to making an existing iPhone app feel native on iPhone Duo. It combines Apple's guidance with field notes from shipping a real SwiftUI app to the Duo: a timer-led fitness app that was portrait-only before this work.

Apple's framing is the most important idea here: **this is a resizability problem, not a new-device problem.** Almost nothing below asks for Duo-specific code. It asks for layouts that stop assuming a 402-point-wide portrait phone. The one exception is the fold, and §5 covers how to handle it without special-casing the device.

> **How to use this**
> - **People:** read §1–§3, then skim §5 and §6. They cover what the documentation doesn't tell you.
> - **Coding agents:** run the audit in §10 against the repo, then work through §3 in order, using §4 for the API names and §5 for patterns. Never add device or pose checks (§2, rules 1 and 4). Report anything this guide gets wrong.

---

## 1. The device in numbers

| Display | Points (3×) | Size classes | Notes |
|---|---|---|---|
| Outer (closed), 5.4" | 466 × 678 | portrait compact/regular, landscape compact/compact | Wider and about 200 pt shorter than a 6.3" iPhone (402 × 874). Status bar, navigation, toolbars and the tab bar can move to a **vertical bar on the side**. Honours `UISupportedInterfaceOrientations`. The outer camera always occludes part of the display. |
| Inner (open), 7.6" | 669 × 951 | regular/regular in both orientations | **Ignores the orientation lock.** Bars are horizontal in portrait and vertical on the side in landscape. Split View runs two apps 50/50. The inner camera occludes only while it's active. |

Both displays have an aspect ratio of 1.42. The poses are closed, partly folded (a "book" in landscape, "seated" in portrait), flat, and propped up like a tent.

**Where the fold actually is (measured in the Device Hub simulator):**
- **Portrait, partly folded:** a horizontal band **40 pt tall at y = 455–495** of the 951-pt screen.
- **Landscape:** a vertical band **40 pt wide at x = 455–495**. The side bar (about 85 pt) takes the trailing edge, so **the fold isn't centred in your content area**. In our app the leading page was about 455 pt wide and the trailing page about 370 pt.
- Always read the fold in your own view's coordinates (§4). The numbers above are for orientation only. A view that starts 82 pt down the screen sees the fold 82 pt higher.

**The SDK gate.** How your app looks on the Duo depends on the SDK it was built with:
- **iOS 26 SDK or older:** compatibility mode. The app sits in a safe area on a **black background**.
- **iOS 27.0 SDK:** uses much more of the display, but leaves some blank space. Bars never go vertical.
- **iOS 27.1 SDK:** full edge-to-edge layout, under the status bar and camera, with vertical bars.

([9to5Mac, Sep 9](https://9to5mac.com/2026/09/09/heres-how-iphone-duo-treats-apps-not-optimized-for-the-foldable-display/).) Arrangement views, reserved regions and the Device Hub simulator are 27.1-only too. **Rebuilding with Xcode 27.1 is most of the visible win.** Do it before writing any clever code.

A portrait-locked, iPhone-only app has never been drawn at regular width or in landscape. On the Duo's inner display it will be, from day one.

## 2. Five rules

1. **Lay out from size classes and your container's size.** Never from the screen size, the device idiom or the interface orientation.
2. **Prefer system containers.** `NavigationStack`, `NavigationSplitView`, `TabView`, `List`, `ScrollView`, `UINavigationController` and `UITabBarController` adapt to every pose for free. Hand-rolled toolbars and tab bars don't.
3. **Keep interactive content inside the safe area; let backgrounds bleed.** Safe areas on the Duo are **asymmetric**. Read each edge on its own and never assume the opposite inset matches.
4. **Never tie a feature or a control to a pose.** The same hierarchy and features closed, open and folded. Special layouts are for hands-free use, and even then nothing disappears.
5. **Keep controls, timers and headlines off the fold.** System components (buttons in bars, sheets, alerts, menus) already avoid it. Scrolling content may cross it.

## 3. Checklist

### Phase 0: audit (any SDK, about 30 minutes per app)
Run the script in §10 (or `scripts/duo-audit.sh`). Then open every screen, sheet and popover at 466 × 678 and at 669 × 951, in both orientations. Until you have the 27.1 simulator, an iPad simulator in full screen stands in for regular width.

### Phase 1: works with the current SDK
- [ ] **Remove screen-based layout.** Replace `UIScreen.main`, `userInterfaceIdiom`, `isPad`/`isPhone` and orientation branches with size classes and container sizes.
- [ ] **Give every toolbar item both a symbol and a title.**
  - A vertical bar shows the icon.
  - A horizontal bar prefers the icon and falls back to the title.
  - The overflow menu shows both.
  - A title-only item, or a custom view, is never shown in a vertical bar.
- [ ] **Audit fixed sizes.**
  - `.frame(width: 340)` on anything on screen is a bug on a folding phone. Off-screen render canvases are fine.
  - Fixed *heights* for hero visuals are a quieter version of the same bug. A 260-pt timer ring looks small on the 669-pt inner display (§5.7).
- [ ] **Audit `ignoresSafeArea`.**
  - Backgrounds and maps may bleed; interactive overlays may not.
  - Scope it to the edges you need, for example `.ignoresSafeArea(edges: [.top, .horizontal])`.
  - A `GeometryReader` that subtracts `safeAreaInsets` is a defect. Reading `.size` is fine.
  - For a photo hero under a bar, use `backgroundExtensionEffect()` (iOS 26).
- [ ] **Cap the width of readable text at regular width** (a 669-pt column of body text is too wide). Keep heroes full-bleed.
- [ ] **Consider a split view** where the app is a list with a detail view. `NavigationSplitView` shows both panes when open and collapses when closed. Keep the selection above the split, so folding doesn't lose it.
- [ ] **Camera:** adopt `AVCaptureDeviceRotationCoordinator` so photos stay upright as the device opens and rotates.
- [ ] **Short screens:** the outer display is only 678 pt tall. Make sure primary buttons never scroll off (§6).
- [ ] **Rebuild with Xcode 27.1 and look again.**

### Phase 2: needs the iOS 27.1 SDK
- [ ] **Sheets.**
  - On the outer display, sheet toolbars go vertical by default. For a sheet whose toolbar is a single Done or Close, opt out: `toolbarVerticalBehavior(.disabled)` / `preferredVerticalBarBehavior = .disabled`.
  - On the inner display, `presentationPlacement(_:)` decides the orientation: trailing placement gets a vertical toolbar; centred and leading get horizontal.
- [ ] **Overflow.** Set `visibilityPriority` so frequently used actions overflow last, and put rare items straight into the overflow menu.
- [ ] **Compression.** `toolbarVerticalCompressionBehavior` chooses whether the toolbar or the tab bar collapses first.
- [ ] **Fold-aware layout for custom screens** (§5): use reserved regions, or arrangement views where the app has a genuine two-up layout.
  - Never nest an arrangement view inside a split view, list or scroll view.
- [ ] **Custom toolbar content:** read `toolbarVerticalEdge` / `verticalBarEdge`. Flexible spacers collapse to zero in a vertical bar.
- [ ] **Tab bar as a sidebar** (`.defaultTabBarPlacement(.sidebar)`) on the inner display: decide per app.
- [ ] **Live Activities** on the side Dynamic Island: verify them, don't assume.
- [ ] **Split View at half width** and Picture in Picture.

### Phase 3: store and launch
- [ ] **Duo screenshots:** outer 1398 × 2034, inner 2007 × 2853 (both also available in landscape). These slots are optional. Apple's Figma and Sketch Duo kits are in Apple Design Resources.
- [ ] **A featuring nomination** in App Store Connect, if the Duo work is substantial (§8).
- [ ] **What's New:** decide whether to mention the Duo there.

## 4. API quick reference

| Need | SwiftUI | UIKit |
|---|---|---|
| Size class | `@Environment(\.horizontalSizeClass)` | `traitCollection.horizontalSizeClass` |
| Fold and camera regions | `GeometryProxy.reservedRegions(kind: .division / .occlusion, options: .includeInactive)` | `UIView.reservedRegions(kind:options:)` |
| Two-up layout | `ArrangementView` + `.arrangementViewStyle(.split / .overlay)` | `UIArrangementViewController` |
| Overlay fold state | `@Environment(\.overlayArrangementZIndex)` | `state(for: .primary)?.zIndex` |
| Item in or out of a vertical bar | `.axisBehavior(.verticalPreferred / .horizontalOnly)` | `item.axisBehavior` |
| Overflow order | `.visibilityPriority(_:)` | `item.visibilityPriority` |
| Explicit overflow | `ToolbarOverflowMenu` | `navigationItem.additionalOverflowItems` |
| Which bar compresses first | `toolbarVerticalCompressionBehavior` | `verticalBarCompressionBehavior` |
| Opt out of vertical bars | `.toolbarVerticalBehavior(.disabled)` | `preferredVerticalBarBehavior = .disabled` |
| Which edge holds the bar | `@Environment(\.toolbarVerticalEdge)` | `traitCollection.verticalBarEdge` |
| Hero under a bar | `backgroundExtensionEffect()` | `UIBackgroundExtensionView` |
| Hinge angle (effects only) | `onHingeChange` | `UIHingeInteraction` |
| Tab bar as sidebar | `.defaultTabBarPlacement(.sidebar)` | sidebar preference placement |
| Upright photos | `AVCaptureDeviceRotationCoordinator` | same |

Everything in Phase 2 is **iOS 27.1+** and can't be back-deployed. Gate it with `#available`.

**Hinge data is for effects and interactions, not layout.** Apple is explicit about this. Layout comes from reserved regions and arrangement views.

## 5. Fold-aware patterns

These are the patterns that held up across every pose in a shipped app. Each one uses the fold region, never a device or pose check, so it degrades to your normal layout everywhere else.

### 5.1 One helper for the fold

```swift
/// The fold, from iOS 27.1 reserved regions.
enum DuoFold {
    /// The fold in `proxy`'s coordinates, active or not, so the layout
    /// doesn't jump as the phone opens and closes.
    static func region(in proxy: GeometryProxy) -> CGRect? {
        if #available(iOS 27.1, *) {
            return proxy.reservedRegions(kind: .division, options: .includeInactive).first?.frame
        }
        return nil
    }

    /// A vertical fold (landscape "book") with a usable page on each side.
    static func side(in proxy: GeometryProxy, minPage: CGFloat = 280) -> CGRect? {
        guard let fold = region(in: proxy),
              fold.height > fold.width,
              fold.minX >= minPage,
              proxy.size.width - fold.maxX >= minPage
        else { return nil }
        return fold
    }
}
```

Use **`.includeInactive`**. Without it, the layout rearranges itself the moment someone bends a flat phone, which feels broken. With it, the layout depends only on the orientation.

### 5.2 Portrait, partly folded: the focal element above, the controls below

A timer, a camera preview or a chart goes above the hinge. The details and buttons go below it, where the thumb rests when the phone is propped up.

```swift
GeometryReader { proxy in
    if let fold = DuoFold.region(in: proxy), fold.width > fold.height,
       fold.minY > 300, proxy.size.height - fold.maxY > 280 {
        VStack(spacing: fold.height) {
            timerRing.frame(height: fold.minY)
            VStack { details; Spacer(); controls }
        }
    } else {
        normalLayout
    }
}
```

**Size the focal element from the space above the fold.** Our first try squeezed a title and a fixed-size ring into that space and got a small ring. Moving the title below the fold and letting the ring fill its half fixed it.

### 5.3 Landscape: two pages, like a book

When the fold is vertical, every custom screen becomes two pages. Give each page its own purpose; don't split one column in half.

| Screen | Leading page | Trailing page |
|---|---|---|
| Running session | timer ring | table, progress, controls |
| Onboarding step | headline, chart or visual | choices + primary button |
| Paywall | the offer and social proof | plans + purchase button |
| Home | your plan: streak, program, today | the library of workouts |
| Progress | the chart | series and range pickers |
| Completion | photo or celebration | message + Close |

Put the **primary action on the trailing page**, where the footer lives. In a scaffold that owns the footer, constrain the footer to that page:

```swift
footer()
    .frame(width: sideFold.map { proxy.size.width - $0.maxX })
    .frame(maxWidth: .infinity, alignment: sideFold == nil ? .center : .trailing)
```

**Lesson learned:** aligning a two-column grid's gutter to the fold is *not* enough. It left short cards stranded beside tall ones and made the columns uneven. Designing two pages with different jobs worked.

### 5.4 Centred cards and dialogs: centre them on one page

A custom celebration card centred on the screen straddles the fold in landscape. Centre it on a page instead:

```swift
extension View {
    func centeredOnDuoPage(_ edge: HorizontalEdge = .trailing) -> some View {
        modifier(DuoPageCentering(edge: edge))
    }
}

private struct DuoPageCentering: ViewModifier {
    let edge: HorizontalEdge
    func body(content: Content) -> some View {
        GeometryReader { proxy in
            if let fold = DuoFold.side(in: proxy) {
                let x = edge == .leading ? 0 : fold.maxX
                let width = edge == .leading ? fold.minX : proxy.size.width - fold.maxX
                content.frame(width: width, height: proxy.size.height).offset(x: x)
            } else {
                content.frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }
}
```

Transparent `GeometryReader` areas don't intercept taps, so a dimmed "tap to dismiss" backdrop behind the card keeps working.

### 5.5 Screens inside a scroll view: pass the fold down

A `GeometryReader` inside a `ScrollView` gets no height proposal and measures nothing useful. **Read the fold outside the scroll view** and pass it into the content through the environment, converted to the content's coordinates (subtract the content's padding):

```swift
.environment(\.foldInContent, DuoFold.region(in: proxy)?.offsetBy(dx: 0, dy: -topPadding))
```

Then a small `FoldSplit { above } below: { below } unfolded: { normal }` view inside the content can arrange itself: stacked around a horizontal fold, or side by side around a vertical one.

### 5.6 What may cross the fold

**Fine to leave on the fold:** scrolling lists, charts, calendars, long text, photos, backgrounds, full-bleed heroes, and system sheets.

**Move off the fold:** buttons, toggles, pickers, timers and countdowns, headlines, and text fields.

### 5.7 Size heroes from the space you have

A fixed 260-pt ring is fine on a 402-pt phone and looks lost on the 669-pt inner display. Let it grow, up to a cap, and shrink on short screens. Inside a scroll view a flexible frame won't shrink by itself, so compute the size from the measured height:

```swift
let ring = min(320, max(180, availableHeight - heightOfEverythingElse))
```

We verified the result on an iPhone SE, a 6.3" iPhone, the outer display and the inner display.

## 6. Pitfalls and dead ends

- **The outer display can't mirror your app while it runs on the inner one.** `sceneAccessory` / `ExternalNonInteractiveAccessory` targets *external* displays. An Apple engineer confirmed that `CameraCaptureAccessory` is currently the only way to use both Duo displays at once, and only for camera capture ([forum thread 847993](https://developer.apple.com/forums/thread/847993)). Apple has also said apps must not imitate the system's standing-clock UI.
- **The fold isn't centred** in landscape (§1). Never compute pages as `width / 2`.
- **Reading reserved regions in `onAppear` can return nothing.** Compute them inside `body`, or observe them with `.onChange(of: DuoFold.side(in: proxy), initial: true)`.
- **A regular-width layout is not the same as a folded layout.** Portrait on the inner display is regular width *and* has a horizontal fold. Landscape has a vertical fold. Branch on the fold's orientation, not on the size class alone.
- **System sheets can straddle the fold** in landscape. The system positions them, so keep the content inside them scrollable and move on.
- **The launch screen** gets stretched across both displays' aspect ratios. A `UILaunchScreen` with a plain brand colour ages better than a storyboard with artwork, which can get cropped in half.
- **Screens designed for a 402-pt phone** break in quiet ways at 466 × 678. Watch for:
  - Primary buttons pushed off the bottom.
  - Aspect-fill photos taking the whole screen.
  - Titles truncated to "…".
- **Opinions differ on vertical glyphs.** Adding symbols for vertical bars changes Done into a checkmark and Close into an xmark on every iPhone. That's Apple's own iOS 26 treatment, so keep it everywhere rather than gating it to the Duo.

## 7. Testing on the simulator

**Setting poses:**
- `simctl` can't fold, rotate or switch displays. Set each pose by hand in Xcode's **Device Hub** (with Device Hub frontmost, rotate with Command-Left Arrow and Command-Right Arrow).
- Plan your test runs around handing the device to a person for each pose change.

**Capturing each display:**
- List the displays with `xcrun simctl io <udid> enumerate`. The inner display is the port whose default size is 2007 × 2853; pass its UUID to `--display`. `--display=LCD` captures the outer one.
- Capture with `xcrun simctl io <udid> screenshot --display=<id> out.png`.

**Known limits:**
- **XCUITest on the inner display:** taps work, but its screenshots come back black and `XCUIDevice.orientation` does nothing. Have tests signal the host, and let the host capture with `simctl`.
- **`print` from a `simctl launch --console` session may show nothing.** To inspect live geometry, log with `NSLog` or `Logger`, then read it back with `xcrun simctl spawn <udid> log show --last 1m --predicate 'eventMessage CONTAINS "…"'`.

**A screen catalog makes every pose cheap to check:**
1. Add a debug-only launch variable (for example `PREVIEW_SCREEN=<name>`) that shows any screen on its own, with seeded demo data.
2. Write a script that launches each screen in turn and captures it. That gives you 40+ screens per pose in a few minutes.
3. Draw the fold band onto each capture before reviewing, then look for controls, timers or headlines underneath it.
4. Remember catalog artifacts: a screen shown on its own has nothing to dismiss to, so its Close and Next buttons do nothing there.

**Testing live transitions:**
- Static captures miss what happens when the pose changes while the app is running.
- Run a background loop that captures both displays every 2 seconds while someone folds, rotates and closes the device on each key screen, including mid-timer. Then remove duplicate frames and review.
- It caught layout jumps and state issues that per-pose screenshots never show.

**Resetting state:** to rerun onboarding, uninstall and reinstall the app. Writing preferences from outside the app (`simctl spawn … defaults write`, or editing its plist) gets overwritten by the app's cached preferences.

**Also check regular iPhones:** every fold-aware change must leave them untouched. Check an SE-sized phone, a 6.3" phone and a Max after each change.

## 8. Store and featuring

**Screenshots:**
- Take them with seeded demo data and a clean status bar: `xcrun simctl status_bar <udid> override --time 9:41 --batteryState charged --batteryLevel 100`.
- The simulator doesn't show the pose, so a half-folded screenshot looks like a flat one with a clever layout. Lead with **landscape book-pose** shots, where two pages read as "made for the Duo" at a glance.
- Capture timers mid-phase (ring about half full), not at 0:00.

**App preview:** record on hardware or with a real prop setup. The pose is the story, and a simulator recording can't show it.

**Featuring nomination (App Store Connect, Featuring Nominations):** use the *App Enhancements* type and submit early. What helps:
- a one-line story about why the Duo suits your app's real use (for example, "propped half-folded on a table, the timer faces you above the hinge");
- the specific technologies (reserved regions, vertical bars, accessibility);
- the version and date it ships.

## 9. Apple's sources

- [Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/): the hub.
- [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo): the most precise source. Read it before the videos.
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) in the Human Interface Guidelines.
- Tech Talks, with transcripts on each video page:
  - [Design for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111466/): principles, poses, sheets and multitasking.
  - [Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/): Xcode, Device Hub and general layout.
  - [Raise the bar with iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111462/): the vertical-bar APIs. It's the densest talk.
  - [Strike a pose with adaptive layouts](https://developer.apple.com/videos/play/tech-talks/111463/): arrangement views and reserved regions.
  - [Leverage multiple displays and scenes](https://developer.apple.com/videos/play/tech-talks/111464/): the hinge, scenes and accessories.
  - [Build a great camera experience](https://developer.apple.com/videos/play/tech-talks/111465/): the virtual front camera and the rotation coordinator.

**Xcode's own agent skill.** Xcode 27.1 ships an `app-resizability` skill for its coding assistant, as plain Markdown inside the app bundle (`Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/`).
- It covers `UIScreen` replacement, asymmetric safe areas, orientation and idiom checks, and the scene lifecycle.
- It's UIKit-first, so it's most useful for apps with many `UIScreen` or idiom hits.
- It's Apple's copyrighted material: point your agent at the path rather than copying the text.

## 10. Audit script

This lists signals, not verdicts. A fixed width may be an off-screen canvas, and a `UIScreen` hit may be dead code, so read each hit before changing it.

```bash
D=~/Developer/YourApp
XD=(--exclude-dir=build --exclude-dir=.git --exclude-dir=.build \
    --exclude-dir=DerivedData --exclude-dir=Pods)
c(){ grep -rEo "$1" "$D" --include="*.swift" "${XD[@]}" 2>/dev/null | wc -l; }
echo "screen-based layout : $(c 'UIScreen\.main|UIScreen\.current')"
echo "idiom/orientation   : $(c 'userInterfaceIdiom|isPad|isPhone|UIDevice\.current\.orientation')"
echo "fixed widths        : $(c '\.frame\(width: *[0-9]+')"
echo "fixed heights       : $(c '\.frame\(height: *[0-9]{3}')"
echo "text-only buttons   : $(c 'Button\("(Done|Cancel|Close|Save|Continue)"\)')"
echo "sheets/covers       : $(c '\.sheet\(|fullScreenCover\(')"
echo "split views         : $(c 'NavigationSplitView')"
echo "custom bars         : $(c 'UIToolbar|UITabBar\(|UINavigationBar\(')"
echo "ignoresSafeArea     : $(c 'ignoresSafeArea')"
grep -h "TARGETED_DEVICE_FAMILY\|IPHONEOS_DEPLOYMENT_TARGET" "$D"/*.xcodeproj/project.pbxproj | sort -u
```

## 11. Prompt for a coding agent

> Read this playbook in full before doing anything. Run the §10 audit against this repo and report the numbers. Then work §3 Phase 1, with one commit per checklist item and the tests passing after each. Don't add device- or pose-specific branches (§2, rules 1 and 4); for the fold, use the patterns in §5. Start Phase 2 only if the project builds with the iOS 27.1 SDK. After any layout change, capture the affected screens in each pose (§7) and look at them yourself before calling the change done. Finish by listing anything this playbook got wrong or doesn't cover.

---

*Version 1.0 (2026-09-26). Based on Apple's iPhone Duo documentation and Tech Talks as of iOS 27.1 beta, plus field notes from shipping a SwiftUI app to the Duo. APIs and measurements may change before and after release; check them against Apple's current docs.*
