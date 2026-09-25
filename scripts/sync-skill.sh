#!/usr/bin/env bash
# Copies PLAYBOOK.md and the audit script into the installable skill folder.
# Run after editing either file.
set -e
cd "$(dirname "$0")/.."
cp PLAYBOOK.md skills/iphone-duo/playbook.md
cp scripts/duo-audit.sh skills/iphone-duo/audit.sh
chmod +x skills/iphone-duo/audit.sh
echo "skill synced"
