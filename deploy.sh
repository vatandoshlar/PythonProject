#!/bin/bash

# Deployment script for Telegram Bot
# Usage: ./deploy.sh

echo "🚀 Deploying Telegram Bot to server..."

# Server details
SERVER="alex@172.27.27.63"
PROJECT_DIR="~/telegram-bot"
REPO_URL="https://github.com/vatandoshlar/PythonProject.git"

echo "📡 Connecting to server: $SERVER"
echo "📁 Project directory: $PROJECT_DIR"
echo "🔗 Repository: $REPO_URL"

# Create deployment commands
cat > temp_deploy_commands.sh << 'EOF'
#!/bin/bash

# Server deployment commands
echo "🔧 Setting up Telegram Bot on server..."

# Update system packages
sudo apt update

# Install Python and pip if not installed
sudo apt install -y python3 python3-pip git

# Install required Python packages
pip3 install python-telegram-bot openpyxl

# Create project directory
mkdir -p ~/telegram-bot
cd ~/telegram-bot

# Clone repository
git clone https://github.com/vatandoshlar/PythonProject.git .

# Make setup script executable
chmod +x setup_server.sh

# Run setup script
./setup_server.sh

# Create systemd service file
sudo tee /etc/systemd/system/telegram-bot.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=alex
WorkingDirectory=/home/alex/telegram-bot
Environment=BOT_TOKEN=your_bot_token_here
Environment=ADMIN_CHAT_ID=your_admin_id_here
Environment=GROUP_ID=your_group_id_here
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✅ Server setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /etc/systemd/system/telegram-bot.service"
echo "2. Set your BOT_TOKEN, ADMIN_CHAT_ID, and GROUP_ID"
echo "3. Run: sudo systemctl daemon-reload"
echo "4. Run: sudo systemctl enable telegram-bot"
echo "5. Run: sudo systemctl start telegram-bot"
echo "6. Check status: sudo systemctl status telegram-bot"
echo ""
echo "🔧 To edit service file:"
echo "sudo nano /etc/systemd/system/telegram-bot.service"
EOF

# Copy commands to server and execute
scp temp_deploy_commands.sh $SERVER:~/deploy_commands.sh
ssh $SERVER "chmod +x ~/deploy_commands.sh && ~/deploy_commands.sh"

# Clean up
rm temp_deploy_commands.sh

echo "✅ Deployment commands sent to server!"
echo ""
echo "📋 Manual steps on server:"
echo "1. SSH to server: ssh alex@172.27.27.63"
echo "2. Edit service file: sudo nano /etc/systemd/system/telegram-bot.service"
echo "3. Set your environment variables"
echo "4. Start service: sudo systemctl start telegram-bot"
