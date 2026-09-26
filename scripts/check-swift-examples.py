#!/usr/bin/env python3
"""Type-check the actual §5 snippets, supplying only their documented view placeholders.

Requires a selected Xcode with the iOS 27.1 SDK or newer. No simulator is booted;
this checks syntax/availability, not runtime layout, state continuity or RTL visuals.
"""
from pathlib import Path
import platform
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def snippet(text, section):
    segment = text.split(f"### {section} ", 1)[1].split("\n### ", 1)[0]
    blocks = re.findall(r"```swift\n(.*?)\n```", segment, re.DOTALL)
    if len(blocks) != 1:
        raise SystemExit(f"Expected exactly one Swift example in §{section}")
    return blocks[0]


def main():
    text = (ROOT / "PLAYBOOK.md").read_text(encoding="utf-8")
    sdk = subprocess.check_output(
        ["xcrun", "--sdk", "iphonesimulator", "--show-sdk-path"], text=True).strip()
    version = subprocess.check_output(
        ["xcrun", "--sdk", "iphonesimulator", "--show-sdk-version"], text=True).strip()
    if tuple(map(int, version.split(".")[:2])) < (27, 1):
        raise SystemExit("Select Xcode 27.1 or newer; #available cannot fix a missing SDK symbol.")
    arch = "arm64" if platform.machine() == "arm64" else "x86_64"
    source = "import SwiftUI\n" + snippet(text, "5.1") + "\n" + snippet(text, "5.4")
    source += """
struct PortraitExample: View {
    let timerRing = Text("Timer")
    let details = Text("Details")
    let controls = Button("Stop") {}
    let normalLayout = Text("Fallback")
    var body: some View {
""" + snippet(text, "5.2") + "\n}\n}\n"
    source += """
struct FooterExample: View {
    func footer() -> some View { Button("Continue") {} }
    var body: some View {
        GeometryReader { proxy in
            let sideFold = DuoFold.side(in: proxy)
""" + snippet(text, "5.3") + "\n}\n}\n}\n"
    source += """
func ringSize(availableHeight: CGFloat, heightOfEverythingElse: CGFloat) -> CGFloat {
""" + snippet(text, "5.7") + "\nreturn ring\n}\n"
    with tempfile.TemporaryDirectory(prefix="duo-swift-check-") as directory:
        path = Path(directory) / "Examples.swift"
        path.write_text(source, encoding="utf-8")
        for target in ("17.0", "27.1"):
            subprocess.run([
                "xcrun", "swiftc", "-typecheck", "-swift-version", "6", "-sdk", sdk,
                "-target", f"{arch}-apple-ios{target}-simulator",
                "-module-cache-path", str(Path(directory) / "ModuleCache"), str(path)
            ], check=True)
            print(f"§5.1/5.2/5.3/5.4/5.7 type-check passed: SDK {version}, target iOS {target}")


if __name__ == "__main__":
    main()
