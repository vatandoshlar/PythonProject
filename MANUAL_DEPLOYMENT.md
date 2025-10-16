# Manual Server Deployment Guide

## 🚀 Deploy Telegram Bot to Server

### **Step 1: Connect to Server**
```bash
ssh alex@172.27.27.63
```

### **Step 2: Install Dependencies**
```bash
# Update system
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip git

# Install Python packages
pip3 install python-telegram-bot openpyxl
```

### **Step 3: Clone Repository**
```bash
# Create project directory
mkdir -p ~/telegram-bot
cd ~/telegram-bot

# Clone the repository
git clone https://github.com/vatandoshlar/PythonProject.git .

# Make setup script executable
chmod +x setup_server.sh

# Run setup script
./setup_server.sh
```

### **Step 4: Create Systemd Service**
```bash
# Create service file
sudo nano /etc/systemd/system/telegram-bot.service
```

**Add this content:**
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=alex
WorkingDirectory=/home/alex/telegram-bot
Environment=BOT_TOKEN=YOUR_BOT_TOKEN_HERE
Environment=ADMIN_CHAT_ID=YOUR_ADMIN_ID_HERE
Environment=GROUP_ID=YOUR_GROUP_ID_HERE
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Step 5: Configure Environment Variables**
Edit the service file and replace:
- `YOUR_BOT_TOKEN_HERE` with your actual bot token
- `YOUR_ADMIN_ID_HERE` with your admin chat ID
- `YOUR_GROUP_ID_HERE` with your group ID

### **Step 6: Start the Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable telegram-bot

# Start the service
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

### **Step 7: Verify Deployment**
```bash
# Check if bot is running
sudo systemctl status telegram-bot

# View real-time logs
sudo journalctl -u telegram-bot -f

# Test bot commands
# Send /start to your bot
```

## 🔧 Management Commands

### **Start/Stop/Restart Bot**
```bash
sudo systemctl start telegram-bot
sudo systemctl stop telegram-bot
sudo systemctl restart telegram-bot
```

### **View Logs**
```bash
# View recent logs
sudo journalctl -u telegram-bot

# View real-time logs
sudo journalctl -u telegram-bot -f

# View logs from today
sudo journalctl -u telegram-bot --since today
```

### **Update Bot**
```bash
cd ~/telegram-bot
git pull origin main
sudo systemctl restart telegram-bot
```

## 📊 Database Management

### **Backup Database**
```bash
cd ~/telegram-bot
cp registered_users.json backups/registered_users_$(date +%Y%m%d_%H%M%S).json
```

### **Restore Database**
```bash
cd ~/telegram-bot
cp backups/registered_users_YYYYMMDD_HHMMSS.json registered_users.json
sudo systemctl restart telegram-bot
```

## 🛠️ Troubleshooting

### **Bot Not Starting**
```bash
# Check service status
sudo systemctl status telegram-bot

# Check logs for errors
sudo journalctl -u telegram-bot -n 50

# Test bot manually
cd ~/telegram-bot
python3 bot.py
```

### **Permission Issues**
```bash
# Fix ownership
sudo chown -R alex:alex ~/telegram-bot

# Fix permissions
chmod +x ~/telegram-bot/*.py
chmod +x ~/telegram-bot/*.sh
```

### **Database Issues**
```bash
# Check database file
ls -la ~/telegram-bot/registered_users.json

# Recreate from sample
cd ~/telegram-bot
cp registered_users_sample.json registered_users.json
```

## ✅ Success Indicators

- ✅ Service status: `active (running)`
- ✅ No errors in logs
- ✅ Bot responds to `/start` command
- ✅ Admin commands work (`/stats`, `/export`, etc.)

## 📞 Support

If you encounter issues:
1. Check service status: `sudo systemctl status telegram-bot`
2. View logs: `sudo journalctl -u telegram-bot -f`
3. Test manually: `cd ~/telegram-bot && python3 bot.py`
