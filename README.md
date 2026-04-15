# Ticket Scraper Bot

Monitors floor ticket prices across multiple ticket sites and sends alerts when prices drop below your threshold. Currently supports TickPick and Gametime, with SeatGeek coming soon.

## What it does

- Checks floor ticket prices every 2 hours
- Filters by minimum quantity and maximum price
- Sends alerts to Discord and iMessage when a deal is found
- Runs 24/7 on a server

## Setup

### 1. Clone the repo

git clone https://github.com/YourUsername/ticket-scraper.git
cd ticket-scraper

### 2. Install dependencies

pip install playwright python-dotenv requests
playwright install chromium

### 3. Create your .env file

Copy the example and fill in your credentials:

cp .env.example .env

### 4. Configure .env

DISCORD_WEBHOOK=your_discord_webhook_url
DISCORD_MENTION=@everyone
IMESSAGE_ADDRESS=yournumber@tmomail.net
GMAIL_ADDRESS=yourgmail@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

### 5. Update the event URLs

In scraper.py and sites.py, replace the TickPick and Gametime event URLs and IDs with the show you want to monitor.

### 6. Run it

python3 scraper.py

For 24/7 server usage:

PYTHONUNBUFFERED=1 nohup python3 scraper.py &

## Configuration

| Variable | Description |
|---|---|
| DISCORD_WEBHOOK | Your Discord channel webhook URL |
| DISCORD_MENTION | Who to ping — @everyone, a role ID, or a user ID |
| IMESSAGE_ADDRESS | Your number@carrier.com for iMessage alerts |
| GMAIL_ADDRESS | Gmail used to send iMessage alerts |
| GMAIL_APP_PASSWORD | 16-character Gmail app password |

## Carrier email addresses

- AT&T: number@txt.att.net
- Verizon: number@vtext.com
- T-Mobile: number@tmomail.net
- Cricket: number@sms.cricketwireless.net

## Discord mention formats

- @everyone — pings everyone in the channel
- <@USER_ID> — pings a specific user
- <@&ROLE_ID> — pings a specific role

To get a user or role ID, enable Developer Mode in Discord settings, then right click the user or role and click Copy ID.

## Supported sites

- TickPick — requires Playwright browser session
- Gametime — clean API, no browser needed
- SeatGeek — coming soon

## Notes

- TickPick requires a visible browser session and works best on a local machine
- Gametime works on any server
- iMessage alerts require a Gmail account with 2FA and an App Password
- DigitalOcean blocks SMTP ports so iMessage won't work on their servers — use Telegram or Discord instead