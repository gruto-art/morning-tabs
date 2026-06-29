#!/bin/bash
# Builds a "Morning Tabs.app" bundle on the user's Desktop so the app can be
# launched with a double-click (no Terminal window).

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="${1:-Morning Tabs}"
APP="$HOME/Desktop/$APP_NAME.app"

echo "Installing → $APP"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
mkdir -p "$APP/Contents/Resources"

cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key><string>launcher</string>
    <key>CFBundleIdentifier</key><string>com.morning-tabs.app</string>
    <key>CFBundleName</key><string>$APP_NAME</string>
    <key>CFBundleVersion</key><string>1.0</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
EOF

cat > "$APP/Contents/MacOS/launcher" <<EOF
#!/bin/bash
exec /usr/bin/python3 "$REPO_DIR/opener-app.py"
EOF

chmod +x "$APP/Contents/MacOS/launcher"
echo "Done. Double-click '$APP_NAME.app' on your Desktop to launch."
