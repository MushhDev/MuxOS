#!/bin/bash
# MuxOS Firewall Configuration - UFW Rules

set -e

echo "Configuring MuxOS Firewall..."

# Reset UFW to defaults
ufw --force reset

# Default policies - deny incoming, allow outgoing
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (optional - disabled by default for security)
# ufw allow ssh

# Allow common services
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Gaming ports
ufw allow 27015:27030/tcp  # Steam
ufw allow 27015:27030/udp  # Steam
ufw allow 27036/tcp        # Steam Remote Play
ufw allow 27031:27036/udp  # Steam Remote Play
ufw allow 4380/udp         # Steam voice chat
ufw allow 3478/udp         # Steam P2P
ufw allow 4379/udp         # Steam P2P

# Discord
ufw allow 50000:65535/udp

# Allow local network (adjust subnet as needed)
ufw allow from 192.168.0.0/16
ufw allow from 10.0.0.0/8

# Block common attack vectors
ufw deny 23/tcp    # Telnet
ufw deny 135/tcp   # Windows RPC
ufw deny 139/tcp   # NetBIOS
ufw deny 445/tcp   # SMB
ufw deny 1433/tcp  # MSSQL
ufw deny 3389/tcp  # RDP

# Enable logging
ufw logging on

# Enable firewall
ufw --force enable

echo "Firewall configured successfully!"
ufw status verbose
