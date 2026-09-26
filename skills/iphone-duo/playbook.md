# iPhone Duo Playbook

This is a practical guide to making an existing iPhone app feel native on iPhone Duo. It combines Apple's guidance with field notes from shipping a real SwiftUI app to iPhone Duo: a timer-led fitness app that was portrait-only before this work.

Apple's framing is the most important idea here: **this is a resizability problem, not a new-device problem.** Almost nothing below asks for Duo-specific code. It asks for layouts that stop assuming a 402-point-wide portrait phone. The one exception is the fold, and §5 covers how to handle it without special-casing the device.

> **Status on September 26, 2026**
> - iOS 27.0 and Xcode 27 were released on September 14.
> - **Xcode 27.1 (with the iOS 27.1 SDK) is in beta.** Builds made with it can go to TestFlight, but not to the App Store yet ([App Store Connect release notes](https://developer.apple.com/help/app-store-connect/release-notes/)).
> - iPhone Duo ships with iOS 27.1, available from October 23.
>
> Everything marked "iOS 27.1" below needs the Xcode 27.1 beta today.

> **How to use this**
> - **People:** read §1 to §3, then skim §5 and §6. Sections 5 and 6 cover what Apple's documentation doesn't.
> - **Coding agents:** run the audit in §10 against the repo, then work through §3 in order, using §4 for the API names and §5 for patterns. Never add device or pose checks (§2, rules 1 and 4). Report anything this guide gets wrong.

Every claim that comes from Apple links to the Apple source. Claims marked **(field observation)** come from our own testing on the Xcode 27.1 beta simulator and are not in Apple's documentation.

---

## 1. The device

### The shape

- **Two displays.** A 5.4-inch outer display (closed) and a 7.6-inch inner display (open) ([Apple specs](https://www.apple.com/iphone-duo/specs/)). Apple says both displays share the same aspect ratio.
- **Size classes** ([Tech Talk: Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/)):
  - Outer, portrait: compact width, regular height.
  - Outer, landscape: compact width, compact height.
  - Inner, both orientations: regular width, regular height.
- **Orientation.** The outer display honors `UISupportedInterfaceOrientations`. The inner display **ignores the orientation lock**, so a portrait-only app also runs in landscape there (Tech Talk 111461).
- **Bars on the side.** Status bar, navigation bars, toolbars and the tab bar can move to a **vertical bar on the side**: on the outer display, and on the inner display in landscape. In portrait on the inner display they stay horizontal ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- **Cameras.** The outer camera always occludes part of the outer display. The inner camera occludes only while it's in use ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- **Poses.** Closed; partially folded like a book (landscape) or seated on a table like a laptop (portrait); flat; and standing on its edges, like a tent ([Tech Talk: Design for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111466/)).
- **Multitasking.** Split View runs two apps side by side, 50/50, on the inner display (Tech Talk 111466).

### Numbers for testing only

Apple publishes pixel resolutions, but **no point sizes, scale factor or fold position**. Its guidance is the opposite of hard-coding them:
- Size views relative to their container, not to fixed iPhone dimensions ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- To keep content off the hinge, use the reserved-region APIs, not hard-coded dimensions ([iPhone Duo Group Lab Q&A](https://developer.apple.com/forums/thread/847644)).

Use the numbers below to set up test sizes and capture screenshots. **Never put them in code.**

| | Apple's pixels | Points (derived, assuming 3x) |
|---|---|---|
| Outer display | 1398 × 2034 ([specs](https://www.apple.com/iphone-duo/specs/), [App Store screenshots](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)) | 466 × 678 |
| Inner display | 2007 × 2853 App Store screenshot size ([screenshot specs](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)); the physical panel is 1878 × 2670 ([specs](https://www.apple.com/iphone-duo/specs/)) | 669 × 951 |
| For comparison, a 6.3-inch iPhone | 1206 × 2622 screenshot size | 402 × 874 |

The outer display is 64 pt wider and about 200 pt shorter than a 6.3-inch iPhone. Screens designed for a tall, narrow phone break there first (§6).

**Where the fold was in our testing (field observation, Xcode 27.1 beta simulator):**
- Portrait, partially folded: a horizontal band about 40 pt tall, around y = 455 to 495 of the 951-pt screen.
- Landscape: a vertical band about 40 pt wide, around x = 455 to 495. The side bar (about 85 pt) takes the trailing edge, so **the fold isn't centered in your content area**. In our app the leading page was about 455 pt wide and the trailing page about 370 pt.

Read the fold at runtime, in your own view's coordinates (§4, §5). The region's frame [includes interactive margins](https://developer.apple.com/documentation/swiftui/reservedregion/frame), and when the device is flat the fold region is inactive and zero wide ([Tech Talk: Strike a pose with adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/)).

### The SDK gate

How your app looks on iPhone Duo depends on the SDK it was built with (Tech Talk 111461; [Group Lab Q&A](https://developer.apple.com/forums/thread/847644)):

| Built with | What happens on iPhone Duo |
|---|---|
| Xcode 26 or earlier (iOS 26 SDK) | Closed: the app sits to the left of the status bar and camera. Open: it runs at a familiar iPhone aspect ratio. It never extends under the status bar and camera. |
| Xcode 27.0 (iOS 27.0 SDK) | On the inner display the app extends to the left of the status bar area. Bars stay horizontal. |
| Xcode 27.1 (iOS 27.1 SDK, beta) | Full edge-to-edge layout under the status bar and camera, with vertical bars. |

Arrangement views, reserved regions, the hinge APIs and the vertical-bar APIs need the iOS 27.1 SDK, and so does the iPhone Duo simulator in [Device Hub](https://developer.apple.com/documentation/xcode/device-hub). Device Hub itself shipped in Xcode 27.

**Rebuilding with Xcode 27.1 is most of the visible win.** Do it before writing any clever code. iPhone Duo also honors `UIRequiresFullScreen` (Tech Talk 111461).

A portrait-locked, iPhone-only app has never been drawn at regular width or in landscape. Once you build with the iOS 27 SDK, on the inner display it will be.

## 2. Five rules

1. **Lay out from size classes and your container's size.** Never from the screen size, the device idiom or the interface orientation. `UIScreen.main` is on its way to deprecation (Tech Talk 111461).
2. **Prefer system containers.** `NavigationStack`, `NavigationSplitView`, `TabView`, `List`, `ScrollView`, `UINavigationController` and `UITabBarController` adapt to every pose for free. Hand-rolled toolbars and tab bars don't.
3. **Keep interactive content inside the safe area; let backgrounds bleed.** Safe areas on iPhone Duo are **asymmetric**. Read each edge on its own and never assume the opposite inset matches.
4. **Never tie a feature or a control to a pose.** The same hierarchy and features closed, open and folded. Special layouts are for hands-free use, and even then nothing disappears.
5. **Keep controls, timers and headlines off the fold.** System sheets, alerts, menus and toolbar buttons already avoid it. Scrolling content may cross it (Tech Talk 111466).

Sources: [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo), [HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo).

## 3. Checklist

### Phase 0: audit (any Xcode, about 30 minutes per app)
Run the script in §10 (or `scripts/duo-audit.sh`). Then open every screen, sheet and popover at both display sizes, in both orientations:
- With Xcode 27.1 beta: use the iPhone Duo simulator in Device Hub.
- With Xcode 27: use Device Hub's [resize mode](https://developer.apple.com/documentation/xcode/configuring-the-environment-of-a-simulated-device) to set 466 × 678 and 669 × 951.

### Phase 1: no iOS 27 APIs needed (Xcode 26 or 27)
- [ ] **Remove screen-based layout.** Replace `UIScreen.main`, `userInterfaceIdiom`, `isPad`/`isPhone` and orientation branches with size classes and container sizes.
- [ ] **Give toolbar items both a symbol and a title** ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
  - A vertical bar shows the icon.
  - A horizontal bar prefers the icon and falls back to the title.
  - The overflow menu shows both.
  - By default, a title-only item or a custom view stays in the horizontal layout. A custom view can opt in with `axisBehavior(.verticalPreferred)` (iOS 27.1).
  - Keep actions like Edit as text, as the HIG recommends ([HIG: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)).
- [ ] **Audit fixed sizes.**
  - `.frame(width: 340)` on anything on screen is a bug on a folding phone. Off-screen render canvases are fine.
  - Fixed *heights* for hero visuals are a quieter version of the same bug. A 260-pt timer ring looks small on the inner display (§5.7).
- [ ] **Audit `ignoresSafeArea`.**
  - Backgrounds and maps may bleed; interactive overlays may not.
  - Scope it to the edges you need, for example `.ignoresSafeArea(edges: [.top, .horizontal])`.
  - A `GeometryReader` that subtracts `safeAreaInsets` is a defect. Reading `.size` is fine.
  - For a photo hero under a bar, use [`backgroundExtensionEffect()`][bgext] (iOS 26).
- [ ] **Cap the width of readable text at regular width** (a 669-pt column of body text is too wide). Keep heroes full-bleed.
- [ ] **Use an even number of grid columns** so content divides cleanly around the fold ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- [ ] **Consider a split view** where the app is a list with a detail view. `NavigationSplitView` shows both panes when open and collapses when closed. Keep the selection above the split, so folding doesn't lose it.
- [ ] **Camera:** adopt [`AVCaptureDevice.RotationCoordinator`][rotation] (iOS 17) so photos stay upright as the device opens and rotates.
- [ ] **Short screens:** the outer display is only 678 pt tall. Make sure primary buttons never scroll off (§6).
- [ ] **Rebuild with Xcode 27.1 (beta until iOS 27.1 ships) and look again.**

### Phase 2: iOS 27 APIs
Each item shows the iOS version it needs. Gate every one with `#available`; none of them back-deploy.

- [ ] **Sheets.**
  - On the outer display, sheet toolbars go vertical by default. For a sheet whose toolbar is a single Done or Close, opt out: [`toolbarVerticalBehavior(.disabled)`][tvb] in SwiftUI; in UIKit, override [`preferredVerticalBarBehavior`][pvbb] to return `.disabled` and call `setNeedsUpdateOfVerticalBarConfiguration()` when it changes (iOS 27.1).
  - On the inner display, [`presentationPlacement(_:)`][placement] (iOS 27.0) decides: trailing placement gets a vertical toolbar; centered and leading placements get a horizontal one.
- [ ] **Overflow.** Set [`visibilityPriority`][prio] (iOS 27.0) so frequently used actions overflow last, and put rare items straight into [`ToolbarOverflowMenu`][overflow] (iOS 27.0).
- [ ] **Compression.** [`toolbarVerticalCompressionBehavior(_:)`][compress] (iOS 27.1) chooses whether the tab bar or the toolbar items collapse first.
- [ ] **Fold-aware layout for custom screens** (§5): use [reserved regions][regions], or [arrangement views][arrangement] where the app has a genuine two-up layout (iOS 27.1).
  - Never nest an arrangement view inside a split view, list or scroll view ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- [ ] **Custom toolbar content:** read [`toolbarVerticalEdge`][edge] (iOS 27.1). Flexible spacers collapse to zero in a vertical bar.
- [ ] **Tab bar as a sidebar** on the inner display: `.tabViewStyle(.sidebarAdaptable)` plus [`.defaultTabBarPlacement(.sidebar)`][sidebar] (iOS 27.0). Decide per app.
- [ ] **Camera direction:** if you pick physical front cameras, adopt [`AVCaptureDeviceDirectionCoordinator`][direction] (iOS 27.1). See [Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces).
- [ ] **Live Activities** on the side Dynamic Island: verify them, don't assume. Most app extensions can't run in the Duo simulator yet (Xcode 27.1 beta known issue).
- [ ] **Split View at half width** and Picture in Picture (the app resizes vertically when PiP pins to the top).

### Phase 3: store and launch
- [ ] **Screenshots:** App Store Connect lists iPhone Duo sizes (outer 1398 × 2034, inner 2007 × 2853, both also in landscape) but **can't accept Duo uploads until later this year** ([screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). Apple's iOS 27 UI Kit (Figma, Sketch) and the iPhone Duo product bezel are in [Apple Design Resources](https://developer.apple.com/design/resources/).
- [ ] **A featuring nomination** in App Store Connect, if the Duo work is substantial (§8).
- [ ] **What's New:** decide whether to mention iPhone Duo there.

## 4. API quick reference

| Need | SwiftUI | UIKit | iOS |
|---|---|---|---|
| Size class | `@Environment(\.horizontalSizeClass)` | `traitCollection.horizontalSizeClass` | any |
| Fold and camera regions | [`GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)`][regions] with `.division` / `.occlusion`, `.includeInactive` | [`UIView.reservedRegions(kind:options:)`][uiregions] | 27.1 |
| Two-up layout | [`ArrangementView`][arrangement] + [`.arrangementViewStyle(.split / .overlay)`][arrstyle] | [`UIArrangementViewController`][uiarr] | 27.1 |
| Overlay fold state | [`@Environment(\.overlayArrangementZIndex)`][zindex] | `state(for: .primary)?.zIndex` | 27.1 |
| Item in or out of a vertical bar | [`.axisBehavior(.verticalPreferred / .horizontalOnly)`][axis] | [`UIBarButtonItem.axisBehavior`][uiaxis] | 27.1 |
| Opt out of vertical bars | [`.toolbarVerticalBehavior(.disabled)`][tvb] | override [`preferredVerticalBarBehavior`][pvbb] | 27.1 |
| Which bar compresses first | [`toolbarVerticalCompressionBehavior(_:)`][compress] | [`navigationItem.verticalBarCompressionBehavior`][uicompress] | 27.1 |
| Which edge holds the bar | [`@Environment(\.toolbarVerticalEdge)`][edge] | [`traitCollection.verticalBarEdge`][uiedge] | 27.1 |
| Hinge angle (effects only) | [`onHingeChange(isEnabled:_:)`][hinge] | [`UIHingeInteraction`][uihinge] | 27.1 |
| Sheet placement | [`presentationPlacement(_:)`][placement] | [`UISheetPresentationController.preferredPlacement`][uiplacement] | 27.0 |
| Overflow order | [`.visibilityPriority(_:)`][prio] | [`UIBarButtonItem.visibilityPriority`][uiprio] | 27.0 |
| Explicit overflow | [`ToolbarOverflowMenu`][overflow] | [`navigationItem.additionalOverflowItems`][uioverflow] | 27.0 / 16.0 |
| Prominent action | [`ToolbarItemPlacement.topBarPinnedTrailing`][pinned] | [`navigationItem.pinnedTrailingGroup`][uipinned] | 27.0 / 16.0 |
| Tab bar as sidebar | [`.defaultTabBarPlacement(.sidebar)`][sidebar] | [`tabBarController.sidebar.preferredPlacement = .sidebar`][uisidebar] | 27.0 |
| Hero under a bar | [`backgroundExtensionEffect()`][bgext] | [`UIBackgroundExtensionView`][uibgext] | 26.0 |
| Upright photos | [`AVCaptureDevice.RotationCoordinator`][rotation] | same | 17.0 |
| Camera by direction | [`AVCaptureDeviceDirectionCoordinator`][direction] | same | 27.1 |

**Hinge data is for effects and interactions, not layout** ([Tech Talk: Leverage multiple displays and scenes on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111464/)). Layout comes from reserved regions and arrangement views.

[regions]: https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)
[uiregions]: https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)
[arrangement]: https://developer.apple.com/documentation/swiftui/arrangementview
[arrstyle]: https://developer.apple.com/documentation/swiftui/view/arrangementviewstyle(_:)
[uiarr]: https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller
[zindex]: https://developer.apple.com/documentation/swiftui/environmentvalues/overlayarrangementzindex
[axis]: https://developer.apple.com/documentation/swiftui/toolbarcontent/axisbehavior(_:)
[uiaxis]: https://developer.apple.com/documentation/uikit/uibarbuttonitem/axisbehavior-swift.property
[tvb]: https://developer.apple.com/documentation/swiftui/view/toolbarverticalbehavior(_:)
[pvbb]: https://developer.apple.com/documentation/uikit/uiviewcontroller/preferredverticalbarbehavior
[compress]: https://developer.apple.com/documentation/swiftui/view/toolbarverticalcompressionbehavior(_:)
[uicompress]: https://developer.apple.com/documentation/uikit/uinavigationitem/verticalbarcompressionbehavior
[edge]: https://developer.apple.com/documentation/swiftui/environmentvalues/toolbarverticaledge
[uiedge]: https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge
[hinge]: https://developer.apple.com/documentation/swiftui/view/onhingechange(isenabled:_:)
[uihinge]: https://developer.apple.com/documentation/uikit/uihingeinteraction
[placement]: https://developer.apple.com/documentation/swiftui/view/presentationplacement(_:)
[uiplacement]: https://developer.apple.com/documentation/uikit/uisheetpresentationcontroller/preferredplacement
[prio]: https://developer.apple.com/documentation/swiftui/toolbarcontent/visibilitypriority(_:)
[uiprio]: https://developer.apple.com/documentation/uikit/uibarbuttonitem/visibilitypriority
[overflow]: https://developer.apple.com/documentation/swiftui/toolbaroverflowmenu
[uioverflow]: https://developer.apple.com/documentation/uikit/uinavigationitem/additionaloverflowitems
[pinned]: https://developer.apple.com/documentation/swiftui/toolbaritemplacement/topbarpinnedtrailing
[uipinned]: https://developer.apple.com/documentation/uikit/uinavigationitem/pinnedtrailinggroup
[sidebar]: https://developer.apple.com/documentation/swiftui/view/defaulttabbarplacement(_:)
[uisidebar]: https://developer.apple.com/documentation/uikit/uitabbarcontroller/sidebar-swift.class/preferredplacement
[bgext]: https://developer.apple.com/documentation/swiftui/view/backgroundextensioneffect()
[uibgext]: https://developer.apple.com/documentation/uikit/uibackgroundextensionview
[rotation]: https://developer.apple.com/documentation/avfoundation/avcapturedevice/rotationcoordinator
[direction]: https://developer.apple.com/documentation/avkit/avcapturedevicedirectioncoordinator
[accessory]: https://developer.apple.com/documentation/swiftui/view/sceneaccessory(content:)
[camacc]: https://developer.apple.com/documentation/swiftui/cameracaptureaccessory
[extacc]: https://developer.apple.com/documentation/swiftui/externalnoninteractiveaccessory

## 5. Fold-aware patterns

These patterns held up across every pose in a shipped app. Each one reads the fold region, never a device or pose check, so it falls back to your normal layout everywhere else.

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

Use **`.includeInactive`**. Without it, the layout rearranges itself the moment someone bends a flat phone, which feels broken. With it, the layout depends only on the orientation. Apple suggests inactive regions for high-level layout decisions (Tech Talk 111463). When the device is flat, the region is inactive and zero wide, so the two-page layout simply shows with no gap.

### 5.2 Portrait, partially folded: the focal element above, the controls below

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

### 5.4 Centered cards and dialogs: center them on one page

A custom celebration card centered on the screen straddles the fold in landscape. Center it on a page instead:

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
extension EnvironmentValues {
    @Entry var foldInContent: CGRect? = nil
}

// Outside the ScrollView:
.environment(\.foldInContent, DuoFold.region(in: proxy)?.offsetBy(dx: 0, dy: -topPadding))
```

Then a small view of your own inside the content (we call ours `FoldSplit`, with `above`, `below` and `unfolded` builders) can arrange itself: stacked around a horizontal fold, or side by side around a vertical one.

### 5.6 What may cross the fold

**Fine to leave on the fold:** scrolling lists, charts, calendars, long text, photos, backgrounds and full-bleed heroes.

**Move off the fold:** buttons, toggles, pickers, timers and countdowns, headlines, and text fields.

System sheets, alerts and menus place themselves: when partially folded, sheets slide over to avoid the fold (Tech Talk 111466).

### 5.7 Size heroes from the space you have

A fixed 260-pt ring is fine on a 402-pt phone and looks lost on the inner display. Let it grow, up to a cap, and shrink on short screens. Inside a scroll view a flexible frame won't shrink by itself, so compute the size from the measured height:

```swift
let ring = min(320, max(180, availableHeight - heightOfEverythingElse))
```

We verified the result on an iPhone SE, a 6.3-inch iPhone, the outer display and the inner display.

## 6. Pitfalls and dead ends

- **The outer display can't mirror your app while it runs on the inner one.**
  - [`ExternalNonInteractiveAccessory`][extacc] targets *external* displays, not the outer display.
  - An Apple engineer confirmed that, at present, [`CameraCaptureAccessory`][camacc] (iOS 27.1, registered with [`sceneAccessory(content:)`][accessory]) is the only way to use both iPhone Duo displays at once, and only for camera capture ([forum thread 847993](https://developer.apple.com/forums/thread/847993)).
  - The one other case Apple mentions is AlarmKit alarms, which the system presents ([Group Lab Q&A](https://developer.apple.com/forums/thread/847644)).
- **The fold isn't centered in landscape** (§1). Never compute pages as `width / 2`.
- **Reading reserved regions in `onAppear` can return nothing** (field observation). Apple suggests reading them through `GeometryReader` or `onGeometryChange` (Tech Talk 111463). Our approach: compute them inside `body`, or observe `.onChange(of: DuoFold.side(in: proxy), initial: true)`.
- **A regular-width layout is not the same as a folded layout.** Portrait on the inner display is regular width *and* has a horizontal fold. Landscape has a vertical fold. Branch on the fold's orientation, not on the size class alone.
- **Custom UI over the camera region loses touches** unless you respect the occlusion reserved region ([Group Lab Q&A](https://developer.apple.com/forums/thread/847644)).
- **New windows open only on the inner display.** Use `UIWindowSceneActivationAction` for them (Tech Talk 111464).
- **The launch screen** gets stretched to fit each display and each Split View size (field observation). A `UILaunchScreen` with a plain brand color ages better than a storyboard with artwork, which can get cropped in half.
- **Screens designed for a 402-pt phone** break in quiet ways on the outer display (field observation). Watch for:
  - Primary buttons pushed off the bottom.
  - Aspect-fill photos taking the whole screen.
  - Titles truncated to "…".
- **Symbols change every iPhone, not only iPhone Duo.** Adding symbols for vertical bars turns Done into a checkmark and Close into an xmark on every iPhone. The HIG prefers symbols in toolbars and has a standard Close symbol ([HIG: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)), so keep them everywhere rather than gating them to iPhone Duo.

## 7. Testing on the simulator

**Setting poses:**
- Set each pose with the controls below the device screen in [Device Hub](https://developer.apple.com/documentation/xcode/device-hub), or with Controls > Rotate Left / Rotate Right (Tech Talk 111461).
- We found no `simctl` command that folds or rotates the device (field observation; we haven't tested `simctl io screenConfig power`). Plan test runs around a person changing the pose.
- Xcode 27.1's Previews canvas can switch to the other display.

**Capturing each display (field observation):**
- List the displays with `xcrun simctl io <udid> enumerate`. The inner display is the port whose default size is 2007 × 2853; pass its UUID to `--display`. `--display=LCD` captured the outer one for us.
- Capture with `xcrun simctl io <udid> screenshot --display=<id> out.png`.

**Known limits:**
- **XCUITest on the inner display** (field observation): taps work, but its screenshots come back black and `XCUIDevice.orientation` does nothing. Have tests signal the host, and let the host capture with `simctl`.
- **Xcode 27.1 beta known issues:** StandBy and most app extensions aren't available in the Duo simulator.
- **`print` from a `simctl launch --console` session may show nothing** (field observation). To inspect live geometry, log with `NSLog` or `Logger`, then read it back with `xcrun simctl spawn <udid> log show --last 1m --predicate 'eventMessage CONTAINS "…"'`.

**A screen catalog makes every pose cheap to check:**
1. Add a debug-only launch variable (for example `PREVIEW_SCREEN=<name>`) that shows any screen on its own, with seeded demo data.
2. Write a script that launches each screen in turn and captures it. That gives you 40+ screens per pose in a few minutes.
3. Draw the fold band onto each capture before reviewing, then look for controls, timers or headlines underneath it.
4. Expect catalog quirks: a screen shown on its own has nothing to dismiss to, so its Close and Next buttons do nothing there.

**Testing live transitions:**
- Static captures miss what happens when the pose changes while the app is running.
- Run a background loop that captures both displays every 2 seconds while someone folds, rotates and closes the device on each key screen, including mid-timer. Then remove duplicate frames and review.
- It caught layout jumps and state issues that per-pose screenshots never show.

**Resetting state** (field observation): to rerun onboarding, uninstall and reinstall the app. Writing preferences from outside the app (`simctl spawn … defaults write`, or editing its plist) gets overwritten by the app's cached preferences.

**Also check regular iPhones:** every fold-aware change must leave them untouched. Check an SE-sized phone, a 6.3-inch phone and a Max after each change.

## 8. Store and featuring

**Screenshots** (for when App Store Connect accepts Duo uploads; see §3, Phase 3):
- Take them with seeded demo data and a clean status bar: `xcrun simctl status_bar <udid> override --time 9:41 --batteryState charged --batteryLevel 100`.
- The simulator doesn't show the pose, so a half-folded screenshot looks like a flat one with a clever layout. Lead with **landscape book-pose** shots, where two pages read as "made for iPhone Duo" at a glance.
- Capture timers mid-phase (ring about half full), not at 0:00.

**App preview:** record on hardware or with a real prop setup. The pose is the story, and a simulator recording can't show it. App Store Connect lists iPhone Duo app preview specs, but uploads aren't available yet.

**Featuring nomination** (App Store Connect, Featuring Nominations): use the *App Enhancements* type. Submit at least 3 weeks ahead ([nominate your app for featuring](https://developer.apple.com/help/app-store-connect/manage-featuring-nominations/nominate-your-app-for-featuring)), ideally up to 3 months ([getting featured](https://developer.apple.com/app-store/getting-featured/)). What helps:
- a one-line story about why iPhone Duo suits your app's real use (for example, "propped half-folded on a table, the timer faces you above the hinge");
- the specific technologies (reserved regions, vertical bars, accessibility);
- the version and date it ships.

## 9. Apple's sources

- [Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/): the hub.
- [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo): the most precise source. Read it before the videos.
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) in the Human Interface Guidelines.
- [iPhone Duo Group Lab Q&A](https://developer.apple.com/forums/thread/847644): Apple engineers' answers to developer questions.
- Tech Talks, with transcripts on each video page:
  - [Design for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111466/): principles, poses, sheets and multitasking.
  - [Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/): Xcode, Device Hub, the SDK gate and general layout.
  - [Raise the bar with iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111462/): the vertical-bar APIs. It's the densest talk.
  - [Strike a pose with adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/): arrangement views and reserved regions.
  - [Leverage multiple displays and scenes on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111464/): the hinge, scenes and accessories.
  - [Build a great camera experience for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111465/): the virtual front camera, the rotation coordinator and the direction coordinator.
- [Device Hub](https://developer.apple.com/documentation/xcode/device-hub) and [configuring a simulated device](https://developer.apple.com/documentation/xcode/configuring-the-environment-of-a-simulated-device).
- [App Store screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications).
- [iPhone Duo technical specifications](https://www.apple.com/iphone-duo/specs/).

**Xcode's own agent skill.** Xcode 27.1 ships an `app-resizability` skill for its coding assistant, as plain Markdown inside the app bundle (`Xcode.app/Contents/PlugIns/IDEIntelligenceChat.framework/Versions/A/Resources/`, the `app-resizability` prompt template plus its `.md.packaged` reference files).
- It covers `UIScreen` replacement, asymmetric safe areas, orientation and idiom checks, and the scene lifecycle.
- It started as a UIKit modernization skill and now covers SwiftUI too (Tech Talk 111461).
- It's Apple's copyrighted material: point your agent at the path rather than copying the text.

## 10. Audit script

This lists signals, not verdicts. A fixed width may be an off-screen canvas, and a `UIScreen` hit may be dead code, so read each hit before changing it. The same script is in `scripts/duo-audit.sh`.

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

> Read this playbook in full before doing anything. Run the §10 audit against this repo and report the numbers. Then work §3 Phase 1, with one commit per checklist item and the tests passing after each. Don't add device- or pose-specific branches (§2, rules 1 and 4); for the fold, use the patterns in §5. Start Phase 2 only if the project builds with the iOS 27.1 SDK, and gate each API with `#available` for the iOS version listed in §4. Never hard-code the device numbers from §1. After any layout change, capture the affected screens in each pose (§7) and look at them yourself before calling the change done. Finish by listing anything this playbook got wrong or doesn't cover.

---

*Version 1.1 (2026-09-26). Checked against Apple's iPhone Duo documentation, Human Interface Guidelines, Tech Talks, API reference and the Group Lab Q&A as of Xcode 27.1 beta (27A9269) and the iOS 27.1 beta SDK, plus field notes from shipping a SwiftUI app to iPhone Duo. APIs and behavior may change before and after release; check them against Apple's current docs.*
