#!/bin/bash
# MuxOS Intrusion Detection Setup

set -e

echo "Setting up MuxOS Intrusion Detection System..."

# Install required packages
apt-get update
apt-get install -y rkhunter chkrootkit aide auditd

# Configure rkhunter (rootkit hunter)
echo "Configuring rkhunter..."
rkhunter --update
rkhunter --propupd

cat > /etc/default/rkhunter <<EOF
CRON_DAILY_RUN="true"
CRON_DB_UPDATE="true"
APT_AUTOGEN="true"
REPORT_EMAIL="root"
EOF

# Configure chkrootkit
echo "Configuring chkrootkit..."
cat > /etc/chkrootkit.conf <<EOF
RUN_DAILY="true"
RUN_DAILY_OPTS="-q"
DIFF_MODE="true"
EOF

# Initialize AIDE (Advanced Intrusion Detection Environment)
echo "Initializing AIDE database..."
aideinit
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Configure audit rules
echo "Configuring audit rules..."
cat > /etc/audit/rules.d/muxos-security.rules <<EOF
# Delete all existing rules
-D

# Set buffer size
-b 8192

# Monitor authentication files
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/sudoers -p wa -k identity
-w /etc/sudoers.d/ -p wa -k identity

# Monitor SSH configuration
-w /etc/ssh/sshd_config -p wa -k sshd

# Monitor system calls for privilege escalation
-a always,exit -F arch=b64 -S execve -k exec
-a always,exit -F arch=b32 -S execve -k exec

# Monitor failed login attempts
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins

# Monitor network configuration
-w /etc/hosts -p wa -k network
-w /etc/network/ -p wa -k network

# Monitor cron
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# Monitor kernel modules
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules

# Make configuration immutable
-e 2
EOF

# Restart auditd
systemctl enable auditd
systemctl restart auditd

# Create daily security check script
cat > /usr/local/bin/muxos-security-check <<'EOF'
#!/bin/bash
# MuxOS Daily Security Check

LOG_FILE="/var/log/muxos-security-check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== Security Check: $DATE ===" >> $LOG_FILE

# Check for rootkits
echo "Running rootkit scan..." >> $LOG_FILE
rkhunter --check --skip-keypress --report-warnings-only >> $LOG_FILE 2>&1

# Check file integrity
echo "Checking file integrity..." >> $LOG_FILE
aide --check >> $LOG_FILE 2>&1

# Check for failed login attempts
echo "Checking for failed logins..." >> $LOG_FILE
grep "Failed password" /var/log/auth.log | tail -20 >> $LOG_FILE 2>&1

# Check listening ports
echo "Checking open ports..." >> $LOG_FILE
ss -tuln >> $LOG_FILE 2>&1

# Check for suspicious processes
echo "Checking processes..." >> $LOG_FILE
ps aux --sort=-%cpu | head -20 >> $LOG_FILE 2>&1

# Send notification if issues found
if grep -q "Warning" $LOG_FILE; then
    notify-send "Security Alert" "Issues found in daily security check. Check $LOG_FILE"
fi
EOF

chmod +x /usr/local/bin/muxos-security-check

# Add to cron
echo "0 4 * * * root /usr/local/bin/muxos-security-check" > /etc/cron.d/muxos-security

echo ""
echo "Intrusion Detection System configured!"
echo "- rkhunter: Rootkit detection"
echo "- chkrootkit: Additional rootkit checks"
echo "- AIDE: File integrity monitoring"
echo "- auditd: System call auditing"
echo ""
echo "Daily security checks will run at 4:00 AM"
