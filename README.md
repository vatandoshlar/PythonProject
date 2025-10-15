# PythonProject

## Telegram Bot + Mini App

This repository contains a Telegram bot (python-telegram-bot v20) and a Telegram Mini App (Flask + static web) that implement the same registration flow.

### Environment
- BOT_TOKEN
- ADMIN_CHAT_ID
- GROUP_ID
- WEBAPP_URL (e.g. https://your-domain/)

### Run Mini App locally
```
pip install -r requirements.txt
export BOT_TOKEN=...
export ADMIN_CHAT_ID=...
export GROUP_ID=...
export WEBAPP_URL=http://localhost:8080/
python app.py
```
Open the mini app at http://localhost:8080/.

### Bot
Run the bot as usual:
```
python bot.py
```
The /start menu contains a button to open the mini app.
