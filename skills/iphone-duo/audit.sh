#!/usr/bin/env bash
# Counts regex occurrences, not defects. Single-line patterns are not a Swift parser.
# Usage: scripts/duo-audit.sh /path/to/YourApp [--details]
set -uo pipefail
D="${1:-.}"
details="${2:-}"
if [ "$#" -gt 2 ] || { [ -n "$details" ] && [ "$details" != --details ]; }; then
  echo "Usage: $0 /path/to/YourApp [--details]" >&2
  exit 2
fi
if [ ! -d "$D" ]; then echo "No such folder: $D" >&2; exit 1; fi
# An absolute root also prevents a dash-prefixed path being interpreted as an option.
D=$(cd "$D" && pwd -P) || exit 1
XD=(--exclude-dir=build --exclude-dir=.git --exclude-dir=.build
    --exclude-dir=DerivedData --exclude-dir=Pods --exclude-dir=.worktrees)

report() {
  local label="$1" pattern="$2" matches status count=0
  matches=$(grep -rEo --include='*.swift' "${XD[@]}" -- "$pattern" "$D")
  status=$?
  if [ "$status" -gt 1 ]; then
    echo "Audit failed while reading Swift sources; counts are incomplete." >&2
    return "$status"
  fi
  if [ -n "$matches" ]; then count=$(printf '%s\n' "$matches" | wc -l | tr -d ' '); fi
  printf '%-20s: %s\n' "$label" "$count"
  if [ "$details" = --details ] && [ "$count" -gt 0 ]; then
    grep -rnE --include='*.swift' "${XD[@]}" -- "$pattern" "$D" || return $?
  fi
}

echo "iPhone Duo audit: $D"
echo "Regex occurrences only; inspect hits before changing code."
report 'screen-based layout' 'UIScreen\.main|UIScreen\.current' || exit $?
report 'idiom/orientation' 'userInterfaceIdiom|isPad|isPhone|UIDevice\.current\.orientation' || exit $?
report 'fixed widths' '\.frame\(width: *[0-9]+' || exit $?
report 'fixed heights' '\.frame\(height: *[0-9]{3}' || exit $?
report 'text-only buttons' 'Button\("(Done|Cancel|Close|Save|Continue)"\)' || exit $?
report 'sheets/covers' '\.sheet\(|fullScreenCover\(' || exit $?
report 'split views' 'NavigationSplitView' || exit $?
report 'custom bars' 'UIToolbar|UITabBar\(|UINavigationBar\(' || exit $?
report 'ignoresSafeArea' 'ignoresSafeArea' || exit $?

echo "Top-level Xcode project settings (not resolved build settings):"
for f in "$D"/*.xcodeproj/project.pbxproj; do
  [ -f "$f" ] || continue
  settings=$(grep -hE 'TARGETED_DEVICE_FAMILY|IPHONEOS_DEPLOYMENT_TARGET' "$f")
  status=$?
  [ "$status" -le 1 ] || exit "$status"
  if [ -n "$settings" ]; then
    printf '%s\n' "$settings" | sed 's/^[[:space:]]*//' | sort -u
  fi
done
# A Swift package or empty folder without a top-level Xcode project is valid.
exit 0
