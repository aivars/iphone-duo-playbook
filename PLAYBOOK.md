# iPhone Duo Playbook

A practical guide to making an existing iPhone app feel native on iPhone Duo.

- **Sources:** Apple's guidance, plus field notes from adapting a released SwiftUI app (a timer-led fitness app, portrait-only before this work) in the iPhone Duo beta simulator.
- **Not yet covered:** validation on shipping Duo hardware. That's a separate check after launch.

**The key idea, in Apple's framing: this is a resizability problem, not a new-device problem.** Almost nothing below asks for Duo-specific code. It asks for layouts that stop assuming a 402-point-wide portrait phone. The one exception is the fold (§5), and even that is handled without special-casing the device.

## At a glance

1. **Rebuild with Xcode 27.1** (§1). Most of the visible win comes from the SDK alone.
2. **Lay out from your container, never the screen** (§2). No device, idiom or pose checks; no hard-coded sizes.
3. **Work the checklist in order** (§3): audit, then fixes that need no new APIs, then iOS 27 APIs, then the store.
4. **Keep controls off the fold** using reserved regions (§5).
5. **Test poses, transitions and accessibility,** not just static screenshots (§7).

> **Status on September 26, 2026**
> - iOS 27.0 and Xcode 27 were released on September 14.
> - **Xcode 27.1 (with the iOS 27.1 SDK) is in beta.** Builds made with it can go to TestFlight, but not to the App Store yet ([App Store Connect release notes](https://developer.apple.com/help/app-store-connect/release-notes/)).
> - iPhone Duo ships with iOS 27.1, available from October 23.
>
> Everything marked "iOS 27.1" below needs the Xcode 27.1 beta today.

> **How to use this**
> - **People:** read §1 to §3, then skim §5 and §6. Sections 5 and 6 cover what Apple's documentation doesn't.
> - **Coding agents:** follow the steps in §11.
>
> **Sources:** every Apple claim links to its Apple source. **(field observation)** marks what we saw in the Xcode 27.1 beta simulator; it isn't in Apple's documentation.

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

**In code, read the fold at runtime** in your own view's coordinates (§4, §5):
- The region's frame [includes interactive margins](https://developer.apple.com/documentation/swiftui/reservedregion/frame).
- When the device is flat, the fold region is inactive and zero wide ([Tech Talk: Strike a pose with adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/)).

### The SDK gate

How your app looks on iPhone Duo depends on the SDK it was built with (Tech Talk 111461; [Group Lab Q&A](https://developer.apple.com/forums/thread/847644)):

| Built with | What happens on iPhone Duo |
|---|---|
| Xcode 26 or earlier (iOS 26 SDK) | Closed: the app sits to the left of the status bar and camera. Open: it runs at a familiar iPhone aspect ratio. It never extends under the status bar and camera. |
| Xcode 27.0 (iOS 27.0 SDK) | On the inner display the app extends to the left of the status bar area. Bars stay horizontal. |
| Xcode 27.1 (iOS 27.1 SDK, beta) | Full edge-to-edge layout under the status bar and camera, with vertical bars. |

**Rebuilding with Xcode 27.1 is most of the visible win.** Do it before writing any clever code.
- **Needs the iOS 27.1 SDK:** arrangement views, reserved regions, the hinge APIs, the vertical-bar APIs, and the iPhone Duo simulator in [Device Hub](https://developer.apple.com/documentation/xcode/device-hub). Device Hub itself shipped in Xcode 27.
- **Portrait-locked apps:** a portrait-locked, iPhone-only app has never been drawn at regular width or in landscape. Once you build with the iOS 27 SDK, it will be, on the inner display.
- **Full-screen apps:** iPhone Duo honors `UIRequiresFullScreen` (Tech Talk 111461).

## 2. Five rules

1. **Lay out from size classes and your container's size.** Never from the screen size, the device idiom or the interface orientation. `UIScreen.main` is on its way to deprecation (Tech Talk 111461).
2. **Prefer system containers.** `NavigationStack`, `NavigationSplitView`, `TabView`, `List`, `ScrollView`, `UINavigationController` and `UITabBarController` adapt for you; hand-rolled toolbars and tab bars need extra work. Still test your content inside them.
3. **Keep interactive content inside the safe area; let backgrounds bleed.** Safe areas on iPhone Duo are **asymmetric**. Read each edge on its own and never assume the opposite inset matches.
4. **Never make a feature available only in one pose.** A secondary pane may collapse into navigation or another presentation, but never remove the user's only route to it. Respond to reserved regions; don't identify the device model or infer a pose from hinge angles.
5. **Keep controls, timers and headlines off the fold.** System sheets, alerts, menus and toolbar buttons already avoid it. Scrolling content may cross it (Tech Talk 111466).

Sources: [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo), [HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo).

## 3. Checklist

### Phase 0: audit (start with a roughly 30-minute triage)
1. **Run the script** in §10. Read the matching code before deciding what to change: counts are not failures.
2. **Open every screen, sheet and popover** at both display sizes, in both orientations:
   - With Xcode 27.1 beta: the iPhone Duo simulator in Device Hub.
   - With Xcode 27: Device Hub's [resize mode](https://developer.apple.com/documentation/xcode/configuring-the-environment-of-a-simulated-device), set to 466 × 678 and 669 × 951.
3. **Plan a full audit later.** A complete screen and accessibility pass takes longer than the triage.

### Phase 1: no iOS 27 APIs needed (Xcode 26 or 27)
- [ ] **Remove screen-based layout assumptions.**
  - Replace screen dimensions, idiom and orientation checks that stand in for available space with size classes and container sizes.
  - Inspect other uses one by one. Don't delete capability checks or non-layout behavior just because a regex matched.
- [ ] **Give toolbar items both a symbol and a title** ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
  - A vertical bar shows the icon.
  - A horizontal bar prefers the icon and falls back to the title.
  - The overflow menu shows both.
  - By default, a title-only item or a custom view stays in the horizontal layout. A custom view can opt in with `axisBehavior(.verticalPreferred)` (iOS 27.1).
  - Keep actions like Edit as text, as the HIG recommends ([HIG: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)).
- [ ] **Audit fixed sizes.**
  - **Fixed widths** such as `.frame(width: 340)` are a signal to review, not automatically a bug. Icons, bounded cards, controls and off-screen render canvases can be fixed on purpose.
  - **Fix sizes that overflow** the container or block useful adaptation.
  - **Fixed hero heights** too: a 260-pt timer ring may look small on the inner display or crowd controls on a short screen (§5.7).
- [ ] **Audit `ignoresSafeArea`.**
  - Backgrounds and maps may bleed; interactive overlays may not.
  - Scope it to the edges you need, for example `.ignoresSafeArea(edges: [.top, .horizontal])`.
  - Know which bounds a `GeometryReader` measures before using `safeAreaInsets`. Don't subtract insets twice from a container that already respects the safe area; do account for each edge when starting from full-bleed bounds.
  - For a photo hero under a bar, use [`backgroundExtensionEffect()`][bgext] (iOS 26).
- [ ] **Review readable line length at regular width.** Cap text-column width by typography and Dynamic Type, not by a device-width threshold. Keep heroes full-bleed where useful.
- [ ] **Consider even grid column counts** where a fold divides a grid ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Don't force extra columns when content or large text sizes need one column.
- [ ] **Consider a split view** where the app is a list with a detail view. `NavigationSplitView` shows both panes when open and collapses when closed. Keep the selection above the split, so folding doesn't lose it.
- [ ] **Camera:** adopt [`AVCaptureDevice.RotationCoordinator`][rotation] (iOS 17) so photos stay upright as the device opens and rotates.
- [ ] **Short screens:** test the 678-pt outer-display height (§6).
  - Primary actions must stay reachable with large text and the keyboard visible.
  - A pinned action helps, but scrolling is a valid fallback. Don't clip content to fit one screen.
- [ ] **Rebuild with Xcode 27.1 (beta until iOS 27.1 ships) and look again.**

### Phase 2: iOS 27 APIs
Each item shows the iOS version it needs.
- **Build time:** you need an SDK that contains the API. The 27.0 items work with Xcode 27.0; only the 27.1 items need Xcode 27.1.
- **Run time:** guard calls with `#available` when your deployment target is older than the API. A guard doesn't make a 27.1 symbol compile with the 27.0 SDK.
- **Fallbacks:** keep useful behavior on older OS versions. Don't raise the deployment target just to copy an example.

- [ ] **Sheets.**
  - On the outer display, sheet toolbars go vertical by default. For a sheet whose toolbar is a single Done or Close, opt out (iOS 27.1):
    - SwiftUI: [`toolbarVerticalBehavior(.disabled)`][tvb].
    - UIKit: override [`preferredVerticalBarBehavior`][pvbb] to return `.disabled`, and call `setNeedsUpdateOfVerticalBarConfiguration()` when it changes.
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
- [ ] **Screenshots:** App Store Connect lists iPhone Duo sizes but **can't accept Duo uploads until later this year** ([screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
  - Sizes: outer 1398 × 2034, inner 2007 × 2853, both also in landscape.
  - Apple's iOS 27 UI Kit (Figma, Sketch) and the iPhone Duo product bezel are in [Apple Design Resources](https://developer.apple.com/design/resources/).
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

- **Evidence:** beta-simulator testing of an existing app, not physical-device validation.
- **Approach:** each pattern reads the fold region instead of identifying a device model or pose.
- **Building blocks, not screens:** names such as `timerRing`, `details`, `controls` and `normalLayout` stand for your own views.
- **Build requirement:** the reserved-region examples need the iOS 27.1 SDK to compile, even though the helper returns `nil` on older iOS versions.
- **State:** keep stateful models above conditional layout branches, so resizing doesn't restart sessions or discard input. Verify it in §7.

### 5.1 One helper for the fold

```swift
/// The fold, from iOS 27.1 reserved regions.
enum DuoFold {
    /// Includes inactive divisions to keep this example's two-page structure
    /// when flat. Mirrored coordinates match SwiftUI's semantic layouts.
    static func region(in proxy: GeometryProxy) -> CGRect? {
        if #available(iOS 27.1, *) {
            return proxy.reservedRegions(
                kind: .division,
                options: .includeInactive,
                layoutDirectionBehavior: .mirrors
            ).first?.frame
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

**Inactive regions: choose deliberately.**
- This helper includes them, to keep a two-page structure when the device is flat. When flat, the fold region is inactive with zero thickness.
- Apple suggests inactive regions for high-level decisions such as grid column counts (Tech Talk 111463).
- To split only when folding makes it useful, query active regions (omit `.includeInactive`) or use an arrangement view.
- A deliberate, state-preserving transition is fine. Avoiding every layout change isn't a requirement.

**Coordinates: mirrored by default** ([reserved-region API][regions]).
- Use them with semantic layouts: `HStack`, `.leading` and `.trailing`, as in §5.4.
- Don't mix them with physical-left assumptions or raw x offsets.
- For manual positioning, request `layoutDirectionBehavior: .fixed`, map semantic edges to physical sides with `layoutDirection`, and don't mirror twice.
- Test RTL and LTR, with asymmetric insets.

**Limits of this example.**
- It uses the first division only. General-purpose layouts must handle every relevant division.
- The `280`-point minimum is a content-fit example, not a hardware dimension. Adapt it to your content and Dynamic Type.

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

When a vertical fold leaves room for two pages, give each page its own purpose; don't split one column in half. The table shows examples from a timer-led app, not rules for every screen.

| Screen | Leading page | Trailing page |
|---|---|---|
| Running session | timer ring | table, progress, controls |
| Onboarding step | headline, chart or visual | choices + primary button |
| Paywall | the offer and social proof | plans + purchase button |
| Home | your plan: streak, program, today | the library of workouts |
| Progress | the chart | series and range pickers |
| Completion | photo or celebration | message + Close |

In this design the **primary action is on the trailing page**, where the footer lives; in your app, keep actions next to the content they act on. To pin a footer to that page (RTL-safe, using the helper's mirrored coordinates):

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
                HStack(spacing: fold.width) {
                    if edge == .leading {
                        content.frame(width: fold.minX, height: proxy.size.height)
                    } else {
                        Color.clear.frame(width: fold.minX)
                            .allowsHitTesting(false)
                            .accessibilityHidden(true)
                    }
                    if edge == .trailing {
                        content.frame(width: proxy.size.width - fold.maxX,
                                      height: proxy.size.height)
                    } else {
                        Color.clear.frame(width: proxy.size.width - fold.maxX)
                            .allowsHitTesting(false)
                            .accessibilityHidden(true)
                    }
                }
                .frame(width: proxy.size.width, height: proxy.size.height)
            } else {
                content.frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }
}
```

- **RTL:** `HStack` gives semantic leading and trailing order, matching the mirrored fold coordinates.
- **Hit testing:** the empty page turns off hit testing and accessibility. Backgrounds, gestures and `contentShape` can change that, so verify backdrop dismissal, card taps and VoiceOver focus in the real presentation.
- **Accessibility:** provide an accessible Close action; don't rely on tapping the backdrop alone.
- **Scope:** assumes a bounded overlay, not a self-sizing row in a scroll view.

### 5.5 Scroll views: distinguish viewport from moving content

**Why it's tricky:** a `ScrollView` proposes no fixed size along its scrolling axis, so an unconstrained `GeometryReader` inside it doesn't measure the viewport. Measuring an explicitly sized child, or a child's background, still works.

**Prefer a viewport-based design:**
- Read the fold in a bounded container outside the scroll view.
- Put stationary controls and panes there, and let long-form content scroll normally inside its pane.
- Ordinary scrolling content may cross the fold (§5.6). Don't keep rearranging an article or feed around it.
- Arrangement views belong outside scrolling content, never inside.

If a custom interaction genuinely needs the fold in moving content coordinates:

1. Give the viewport a named coordinate space and measure the content's current origin in that same space, including scrolling and padding.
2. Read the reserved region in the viewport. For manual physical-coordinate arithmetic, request `.fixed` rather than mixing mirrored geometry with an unmirrored origin.
3. For a translation-only hierarchy, subtract **both components of the measured content origin** from the region's origin. Subtracting only `topPadding` is not a conversion once content scrolls or is nested. Scaled or rotated content needs an appropriate transform, not just subtraction.
4. Recompute when geometry, scroll position, safe areas, keyboard or layout direction changes. Do not cache the initial frame or feed a displacement back into its own measurement loop.

Test at nonzero scroll offsets, in LTR and RTL. If this complexity doesn't clearly improve the interaction, use a viewport layout instead.

### 5.6 What may cross the fold

**Fine to leave on the fold:** scrolling lists, charts, calendars, long text, photos, backgrounds and full-bleed heroes.

**Move off the fold:** buttons, toggles, pickers, timers and countdowns, headlines, and text fields.

System sheets, alerts and menus place themselves: when partially folded, sheets slide over to avoid the fold (Tech Talk 111466).

### 5.7 Size heroes from the space you have

A fixed 260-pt ring is fine on a 402-pt phone and looks lost on the inner display. Let it grow, up to a cap, and shrink on short screens. Inside a scroll view a flexible frame won't shrink by itself, so compute the size from the measured height:

```swift
let ring = min(320, max(180, availableHeight - heightOfEverythingElse))
```

- **Tested on:** an iPhone SE-sized simulator, a 6.3-inch iPhone simulator, and both Duo simulator displays.
- **The 180-pt minimum is a preference, not a guarantee of fit.** With less space, use a smaller or scrollable fallback instead of clipping controls.
- **Measure text** at the actual Dynamic Type size.

## 6. Pitfalls and dead ends

- **The outer display can't mirror your app while it runs on the inner one.**
  - [`ExternalNonInteractiveAccessory`][extacc] targets *external* displays, not the outer display.
  - An Apple engineer confirmed that, at present, [`CameraCaptureAccessory`][camacc] (iOS 27.1, registered with [`sceneAccessory(content:)`][accessory]) is the only way to use both iPhone Duo displays at once, and only for camera capture ([forum thread 847993](https://developer.apple.com/forums/thread/847993)).
  - The one other case Apple mentions is AlarmKit alarms, which the system presents ([Group Lab Q&A](https://developer.apple.com/forums/thread/847644)).
- **The fold isn't centered in landscape** (§1). Never compute pages as `width / 2`.
- **Reading reserved regions in `onAppear` can return nothing** (field observation).
  - Apple suggests reading them through `GeometryReader` or `onGeometryChange` (Tech Talk 111463).
  - We compute them inside `body`, or observe `.onChange(of: DuoFold.side(in: proxy), initial: true)`.
- **A regular-width layout is not the same as a folded layout.** Portrait on the inner display is regular width *and* has a horizontal fold. Landscape has a vertical fold. Branch on the fold's orientation, not on the size class alone.
- **Custom UI over the camera region loses touches** unless you respect the occlusion reserved region ([Group Lab Q&A](https://developer.apple.com/forums/thread/847644)).
- **New windows open only on the inner display.** Use `UIWindowSceneActivationAction` for them (Tech Talk 111464).
- **The launch screen gets stretched** to fit each display and each Split View size (field observation). Use a `UILaunchScreen` with a plain brand color; a storyboard with artwork can get cropped in half.
- **Screens designed for a 402-pt phone** break in quiet ways on the outer display (field observation). Watch for:
  - Primary buttons pushed off the bottom.
  - Aspect-fill photos taking the whole screen.
  - Titles truncated to "…".
- **Symbols change every iPhone, not only iPhone Duo.** Adding symbols for vertical bars turns Done into a checkmark and Close into an xmark everywhere. Keep them on all devices rather than gating them to iPhone Duo: the HIG prefers symbols in toolbars and has a standard Close symbol ([HIG: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)).

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

**Resetting state** (field observation):
- Editing preferences from outside the app didn't stick: the app's cached preferences overwrote them.
- Prefer a debug-only in-app reset or launch option, on a dedicated test installation.
- Uninstall and reinstall is the fallback. It deletes that installation's local data but may not reset Keychain or cloud state. Never use it on an installation with data you need.

### Acceptance checks beyond screenshots

- **Dynamic Type and localization:** test the largest accessibility sizes, long translations and both LTR/RTL. Labels and primary actions remain readable and reachable, with a scrolling fallback where needed.
- **VoiceOver and Voice Control:** verify logical reading order, useful control names and focus after folding, rotation and sheet dismissal. Decorative/empty layout regions should not become accessibility elements.
- **Keyboard:** focus fields in sheets and forms; confirm inputs, validation messages and actions remain reachable as the keyboard and bars resize the viewport.
- **Motion and contrast:** check Reduce Motion, light/dark appearances, contrast and meaning conveyed without color alone.
- **State continuity:** during a running timer, audio session or unsaved form, fold, unfold, rotate and enter/leave Split View. Check elapsed time, playback, selection, navigation path, text/focus and scroll position. Layout-only transitions must not restart work, duplicate tasks or lose edits.
- **Real navigation:** test the actual app flow, not only the screen catalog. A catalog with a nonfunctional Close button is not evidence that dismissal works.
- **Hardware follow-up:** record simulator-only limitations and repeat affected checks on a real Duo when available. Record Xcode/runtime versions and distinguish pass, fail, blocked and not tested.

**Also check regular iPhones:** every fold-aware change must leave them untouched. Check an SE-sized phone, a 6.3-inch phone and a Max after each change.

## 8. Store and featuring

**Screenshots** (for when App Store Connect accepts Duo uploads; see §3, Phase 3):
- Take them with seeded demo data and a clean status bar: `xcrun simctl status_bar <udid> override --time 9:41 --batteryState charged --batteryLevel 100`.
- The simulator doesn't show the pose, so a half-folded screenshot looks like a flat one with a clever layout. Lead with **landscape book-pose** shots, where two pages read as "made for iPhone Duo" at a glance.
- Capture timers mid-phase (ring about half full), not at 0:00.

**App Store preview:**
- Use screen recordings of the app itself. [App Review Guideline 2.3.4](https://developer.apple.com/app-store/review/guidelines/#accurate-metadata) allows narration and overlays, but a filmed device or prop demo can't replace the screen capture.
- App Store Connect lists iPhone Duo preview specs, but uploads aren't available yet.

**Separate marketing video:**
- A filmed device can show the fold on your website, on social channels, or in a featuring pitch where that format is accepted.
- Label simulations and props honestly; don't present them as real-device validation.
- Keep it separate from the App Store preview.

**Featuring nomination** (App Store Connect, Featuring Nominations): use the *App Enhancements* type.

**Timing counts back from your own publish date, not from the iPhone Duo launch.** In the form you pick the date or date range your update will publish. Apple asks for:
- at least 2 weeks' notice ([getting featured](https://developer.apple.com/app-store/getting-featured/));
- a recommended minimum of 3 weeks ([nominate your app for featuring](https://developer.apple.com/help/app-store-connect/manage-featuring-nominations/nominate-your-app-for-featuring));
- ideally up to 3 months ahead, for wider consideration ([getting featured](https://developer.apple.com/app-store/getting-featured/)).

There's no Duo-specific nomination deadline. Updates built with the iOS 27.1 SDK can't publish before iOS 27.1 ships, so pick a date range after its release, and nominate as early as you can.

What helps:
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

The maintained script is [`scripts/duo-audit.sh`](https://github.com/aivars/iphone-duo-playbook/blob/main/scripts/duo-audit.sh).
- **Signals, not verdicts.** A fixed width may be intentional, and a screen reference may have nothing to do with layout. Read each hit before changing it.
- **A triage aid, not a Swift parser.** Its single-line regexes can miss multiline calls, constants, localized labels and wrapped APIs.
- **Counts can't certify readiness.**

```bash
./scripts/duo-audit.sh /path/to/YourApp
# Include file and line references for manual inspection:
./scripts/duo-audit.sh /path/to/YourApp --details
```

Run those commands from this repository's root. In the installed skill, use `bash audit.sh /path/to/YourApp --details` from the skill folder instead.

## 11. Prompt for a coding agent

> Read this playbook in full before changing code. Then:
>
> 1. **Audit.** Run the §10 audit, report the numbers, and inspect the hits. They are not automatic defects.
> 2. **Check the setup.** Note the selected SDK, the deployment target and any existing changes.
> 3. **Phase 1.** Work the applicable §3 Phase 1 items in small, reviewable changes, testing each.
> 4. **Phase 2.** Use the 27.0 items with the 27.0 SDK, and the 27.1 items only with the 27.1 SDK or newer. `#available` doesn't make new APIs compile with an older SDK. Keep fallbacks; don't raise the deployment target unless agreed.
> 5. **Layout rules.** Base layout on container geometry and reserved regions, never device-model or hinge-angle pose checks. Keep every feature reachable. Never hard-code the §1 measurements. Choose active-only or inactive-region layout deliberately, and handle coordinates and RTL consistently.
> 6. **State.** Keep state above layout branches that change.
> 7. **Verify.** After layout changes, inspect captures and run the §7 accessibility, keyboard, state-continuity and real-navigation checks on the affected configurations.
> 8. **Stay in scope.** Follow the user's approval rules for commits, publishing and destructive resets.
> 9. **Report.** What changed, what passed, what is blocked or untested, and any errors or gaps in this playbook.

---

*Version 1.3.1 (2026-09-28). Checked against Apple's documentation and Xcode 27.1 beta (27A9269). Field observations come from beta-simulator testing of an existing app, not shipping hardware. APIs and behavior may change: check current docs and rerun affected tests before release.*
