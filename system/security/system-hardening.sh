#!/bin/bash
# MuxOS System Hardening Script

set -e

echo "==================================="
echo "MuxOS Security Hardening"
echo "==================================="

# Kernel hardening via sysctl
echo "Applying kernel security parameters..."
cat > /etc/sysctl.d/99-muxos-security.conf <<EOF
# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP broadcast requests
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Block SYN attacks
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Log Martians
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Disable IPv6 if not needed
# net.ipv6.conf.all.disable_ipv6 = 1

# Restrict kernel pointer access
kernel.kptr_restrict = 2

# Restrict dmesg access
kernel.dmesg_restrict = 1

# Protect against ptrace
kernel.yama.ptrace_scope = 1

# Disable core dumps for security
fs.suid_dumpable = 0
EOF

sysctl -p /etc/sysctl.d/99-muxos-security.conf

# Secure SSH (if installed)
if [ -f /etc/ssh/sshd_config ]; then
    echo "Hardening SSH configuration..."
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/#MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
    sed -i 's/#LoginGraceTime.*/LoginGraceTime 60/' /etc/ssh/sshd_config
    systemctl restart sshd 2>/dev/null || true
fi

# Set secure permissions on sensitive files
echo "Setting secure file permissions..."
chmod 700 /root
chmod 600 /etc/shadow
chmod 644 /etc/passwd
chmod 600 /etc/gshadow
chmod 644 /etc/group

# Disable unnecessary services
echo "Disabling unnecessary services..."
SERVICES_TO_DISABLE=(
    "avahi-daemon"
    "cups"
    "rpcbind"
    "telnet"
)

for service in "${SERVICES_TO_DISABLE[@]}"; do
    systemctl disable "$service" 2>/dev/null || true
    systemctl stop "$service" 2>/dev/null || true
done

# Install and configure fail2ban
if command -v fail2ban-client &> /dev/null; then
    echo "Configuring fail2ban..."
    cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF
    systemctl enable fail2ban
    systemctl restart fail2ban
fi

# Configure automatic security updates
echo "Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF

# Set password policies
echo "Setting password policies..."
if [ -f /etc/login.defs ]; then
    sed -i 's/PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs
    sed -i 's/PASS_MIN_DAYS.*/PASS_MIN_DAYS 1/' /etc/login.defs
    sed -i 's/PASS_MIN_LEN.*/PASS_MIN_LEN 12/' /etc/login.defs
fi

# Secure /tmp
echo "Securing /tmp..."
if ! grep -q "/tmp" /etc/fstab; then
    echo "tmpfs /tmp tmpfs defaults,noexec,nosuid,nodev 0 0" >> /etc/fstab
fi

# Enable AppArmor if available
if command -v apparmor_status &> /dev/null; then
    echo "Enabling AppArmor..."
    systemctl enable apparmor
    systemctl start apparmor
fi

echo ""
echo "==================================="
echo "Security hardening complete!"
echo "==================================="
echo ""
echo "Recommendations:"
echo "1. Review and enable SSH key-only authentication"
echo "2. Set up regular backup schedule"
echo "3. Keep system updated regularly"
echo "4. Review firewall rules periodically"
echo "5. Monitor /var/log for suspicious activity"
