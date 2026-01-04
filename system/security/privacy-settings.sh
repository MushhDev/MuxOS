#!/bin/bash
# MuxOS Privacy Configuration

set -e

echo "Configuring MuxOS Privacy Settings..."

# Disable telemetry and tracking
echo "Disabling telemetry..."

# Block tracking domains
cat >> /etc/hosts <<EOF

# MuxOS Privacy - Block tracking domains
127.0.0.1 analytics.google.com
127.0.0.1 www.google-analytics.com
127.0.0.1 ssl.google-analytics.com
127.0.0.1 telemetry.mozilla.org
127.0.0.1 incoming.telemetry.mozilla.org
127.0.0.1 data.microsoft.com
127.0.0.1 telemetry.microsoft.com
127.0.0.1 vortex.data.microsoft.com
127.0.0.1 settings-win.data.microsoft.com
EOF

# Configure DNS over HTTPS
echo "Configuring encrypted DNS..."
mkdir -p /etc/systemd/resolved.conf.d/
cat > /etc/systemd/resolved.conf.d/dns-over-tls.conf <<EOF
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 9.9.9.9#dns.quad9.net
DNSOverTLS=yes
DNSSEC=yes
EOF

systemctl restart systemd-resolved 2>/dev/null || true

# Configure Firefox privacy settings
FIREFOX_PREFS="/etc/firefox-esr/firefox-esr.js"
if [ -d "/etc/firefox-esr" ]; then
    echo "Configuring Firefox privacy..."
    cat > "$FIREFOX_PREFS" <<EOF
// MuxOS Firefox Privacy Settings
pref("privacy.trackingprotection.enabled", true);
pref("privacy.trackingprotection.socialtracking.enabled", true);
pref("privacy.donottrackheader.enabled", true);
pref("privacy.firstparty.isolate", true);
pref("network.cookie.cookieBehavior", 1);
pref("dom.event.clipboardevents.enabled", false);
pref("media.navigator.enabled", false);
pref("geo.enabled", false);
pref("browser.safebrowsing.malware.enabled", false);
pref("browser.safebrowsing.phishing.enabled", false);
pref("datareporting.healthreport.uploadEnabled", false);
pref("toolkit.telemetry.enabled", false);
pref("toolkit.telemetry.unified", false);
pref("toolkit.telemetry.archive.enabled", false);
pref("browser.newtabpage.activity-stream.feeds.telemetry", false);
pref("browser.newtabpage.activity-stream.telemetry", false);
pref("browser.ping-centre.telemetry", false);
EOF
fi

# MAC address randomization
echo "Configuring MAC address randomization..."
cat > /etc/NetworkManager/conf.d/30-mac-randomization.conf <<EOF
[device]
wifi.scan-rand-mac-address=yes

[connection]
wifi.cloned-mac-address=random
ethernet.cloned-mac-address=random
EOF

# Disable core dumps
echo "Disabling core dumps..."
echo "* hard core 0" >> /etc/security/limits.conf
echo "kernel.core_pattern=|/bin/false" >> /etc/sysctl.d/99-muxos-privacy.conf

# Clear bash history on exit
echo "Configuring shell privacy..."
cat >> /etc/bash.bashrc <<EOF

# MuxOS Privacy - Clear history on exit
export HISTSIZE=1000
export HISTFILESIZE=0
shopt -s histappend
PROMPT_COMMAND='history -a'
trap 'history -c; history -w' EXIT
EOF

# Create privacy cleanup script
cat > /usr/local/bin/muxos-privacy-clean <<'EOF'
#!/bin/bash
# MuxOS Privacy Cleanup

echo "Cleaning privacy-sensitive data..."

# Clear browser data
rm -rf ~/.mozilla/firefox/*.default*/cookies.sqlite
rm -rf ~/.mozilla/firefox/*.default*/places.sqlite
rm -rf ~/.cache/mozilla/firefox/*

# Clear bash history
> ~/.bash_history

# Clear recently used
rm -f ~/.local/share/recently-used.xbel

# Clear thumbnails
rm -rf ~/.cache/thumbnails/*

# Clear temp files
rm -rf /tmp/*
rm -rf ~/.cache/*

echo "Privacy cleanup complete!"
EOF

chmod +x /usr/local/bin/muxos-privacy-clean

echo ""
echo "Privacy configuration complete!"
echo "Run 'muxos-privacy-clean' to manually clear sensitive data"
