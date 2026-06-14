# Personal Finance Tracker Bot

A Telegram bot for tracking personal income, expenses, categories, monthly limits, history, and CSV reports. It is built with async Python, Aiogram 3, PostgreSQL, and asyncpg.

## Commands

| Command | Description |
| --- | --- |
| `/start` | Register or restart the bot |
| `/add` | Add an income or expense transaction |
| `/stats` | Show this month's income, expense, and net balance |
| `/history` | Show the last 10 transactions |
| `/categories` | Manage income and expense categories |
| `/report` | Export this month's transactions to CSV |
| `/limit` | Set or clear a monthly limit for an expense category |
| `/monthly` | Compare income, expense, and net for the last 3 months |
| `/cancel` | Cancel the current action |

Bot username: `<fill after deploy>`

## Tech Stack

- Python 3.11+
- Aiogram 3
- PostgreSQL with asyncpg
- python-dotenv

## Local Setup

### 1. Clone and install dependencies

Windows PowerShell:

```powershell
git clone <repo-url>
cd finance_bot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
git clone <repo-url>
cd finance_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create the PostgreSQL database and user

Using shell tools:

```bash
createdb finance_bot
```

Or with SQL:

```sql
CREATE DATABASE finance_bot;
CREATE USER botuser WITH PASSWORD 'change_me';
GRANT ALL PRIVILEGES ON DATABASE finance_bot TO botuser;
```

If your PostgreSQL version requires schema privileges, connect to the database as an administrator and run:

```sql
GRANT ALL ON SCHEMA public TO botuser;
```

### 3. Configure environment variables

Copy the template and fill in real values:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

### 4. Apply schema

The schema is applied automatically on startup. You can also apply it manually:

```bash
psql -U botuser -d finance_bot -f db/schema.sql
```

### 5. Run the bot

```bash
python bot.py
```

## Environment Variables

| Variable | Description |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `DB_HOST` | PostgreSQL host, usually `localhost` for local development |
| `DB_PORT` | PostgreSQL port, defaults to `5432` if unset |
| `DB_NAME` | Database name, for example `finance_bot` |
| `DB_USER` | PostgreSQL username used by the bot |
| `DB_PASS` | PostgreSQL password for `DB_USER` |

## Deploy on a Linux Server

### screen method

```bash
cd /opt/finance_bot
source venv/bin/activate
screen -S finbot
python bot.py
```

Detach from the session with `Ctrl+A`, then `D`. Reattach later with:

```bash
screen -r finbot
```

### systemd method

Create `/etc/systemd/system/finbot.service`:

```ini
[Unit]
Description=Personal Finance Tracker Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
WorkingDirectory=/opt/finance_bot
ExecStart=/opt/finance_bot/venv/bin/python bot.py
Restart=always
RestartSec=5
EnvironmentFile=/opt/finance_bot/.env

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now finbot
sudo systemctl status finbot
```

View logs:

```bash
journalctl -u finbot -f
```

## Security

The real `.env` file is gitignored and must never be committed. Keep `BOT_TOKEN` and database passwords private, and only commit `.env.example` with placeholders.
