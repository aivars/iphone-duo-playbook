#!/usr/bin/env bash
# iPhone Duo readiness audit. Prints signals, not verdicts: read each hit before changing it.
# Usage: scripts/duo-audit.sh /path/to/YourApp
set -u
D="${1:-.}"
if [ ! -d "$D" ]; then echo "No such folder: $D" >&2; exit 1; fi
XD=(--exclude-dir=build --exclude-dir=.git --exclude-dir=.build \
    --exclude-dir=DerivedData --exclude-dir=Pods --exclude-dir=.worktrees)
c(){ grep -rEo "$1" "$D" --include="*.swift" "${XD[@]}" 2>/dev/null | wc -l | tr -d ' '; }
echo "iPhone Duo audit: $D"
echo "screen-based layout : $(c 'UIScreen\.main|UIScreen\.current')"
echo "idiom/orientation   : $(c 'userInterfaceIdiom|isPad|isPhone|UIDevice\.current\.orientation')"
echo "fixed widths        : $(c '\.frame\(width: *[0-9]+')"
echo "fixed heights       : $(c '\.frame\(height: *[0-9]{3}')"
echo "text-only buttons   : $(c 'Button\("(Done|Cancel|Close|Save|Continue)"\)')"
echo "sheets/covers       : $(c '\.sheet\(|fullScreenCover\(')"
echo "split views         : $(c 'NavigationSplitView')"
echo "custom bars         : $(c 'UIToolbar|UITabBar\(|UINavigationBar\(')"
echo "ignoresSafeArea     : $(c 'ignoresSafeArea')"
for f in "$D"/*.xcodeproj/project.pbxproj; do
  [ -f "$f" ] && grep -h "TARGETED_DEVICE_FAMILY\|IPHONEOS_DEPLOYMENT_TARGET" "$f" | sed 's/^[[:space:]]*//' | sort -u
done
