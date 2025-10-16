#!/bin/bash

# Server Setup Script for Telegram Bot
# This script helps set up the bot on a new server

echo "🚀 Setting up Telegram Bot on server..."

# Check if registered_users.json exists
if [ ! -f "registered_users.json" ]; then
    echo "📁 Creating registered_users.json from sample..."
    cp registered_users_sample.json registered_users.json
    echo "✅ Database file created successfully!"
else
    echo "📊 Database file already exists, keeping existing data."
fi

# Set proper permissions
chmod 644 registered_users.json
echo "🔐 Set proper file permissions"

# Create backup directory
mkdir -p backups
echo "📦 Created backup directory"

# Create log directory
mkdir -p logs
echo "📝 Created logs directory"

echo ""
echo "✅ Server setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set your BOT_TOKEN environment variable"
echo "2. Set your ADMIN_CHAT_ID environment variable"
echo "3. Run: python3 bot.py"
echo ""
echo "🔧 Environment variables:"
echo "export BOT_TOKEN='your_bot_token_here'"
echo "export ADMIN_CHAT_ID='your_admin_id_here'"
echo "export GROUP_ID='your_group_id_here'"
echo ""
echo "📊 Your database is ready with sample data!"
