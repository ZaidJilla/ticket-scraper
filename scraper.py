from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import requests
import smtplib
import time

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
IMESSAGE_ADDRESS = os.getenv("IMESSAGE_ADDRESS")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

PRICE_THRESHOLD = 500
MIN_QUANTITY = 4
CHECK_INTERVAL = 12 * 60 * 60
EVENT_URL = "https://www.tickpick.com/buy-don-toliver-tickets-7718028/"
API_URL = "https://api.tickpick.com/1.0/listings/internal/event-v2/7718028"


def send_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message})
        print("Discord alert sent.")
    except Exception as e:
        print(f"Discord failed: {e}")


def send_imessage(message):
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, IMESSAGE_ADDRESS, message)
        print("iMessage alert sent.")
    except Exception as e:
        print(f"iMessage failed: {e}")


def check_tickets():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        try:
            page.goto(EVENT_URL)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

            data = page.evaluate(f"""
                () => fetch("{API_URL}")
                    .then(r => r.json())
            """)

            listings = data["listings"]
            floor_tickets = []

            for listing in listings:
                if listing.get("lid") == "Floor":
                    price = listing.get("p")
                    quantity = listing.get("q")
                    row = listing.get("r")

                    if quantity >= MIN_QUANTITY and price <= PRICE_THRESHOLD:
                        floor_tickets.append(
                            {"row": row, "price": price, "quantity": quantity}
                        )

            return floor_tickets

        except Exception as e:
            print(f"Error checking tickets: {e}")
            return []

        finally:
            browser.close()


def run():
    print("Bot started. Checking every 12 hours.")
    while True:
        print("Checking tickets...")
        deals = check_tickets()

        if deals:
            cheapest = min(deals, key=lambda x: x["price"])
            message = (
                f"@everyone DON TOLIVER FLOOR ALERT\n"
                f"Row: {cheapest['row']}\n"
                f"Price: ${cheapest['price']}\n"
                f"Quantity: {cheapest['quantity']}\n"
                f"Buy here: {EVENT_URL}"
            )
            send_discord(message)
            send_imessage(message)
        else:
            print(f"No floor tickets found with 4+ quantity under ${PRICE_THRESHOLD}.")

        print("Next check in 12 hours.")
        time.sleep(CHECK_INTERVAL)


run()
