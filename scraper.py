from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import requests
import smtplib
import time
from sites import check_gametime

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
IMESSAGE_ADDRESS = os.getenv("IMESSAGE_ADDRESS")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

PRICE_THRESHOLD = 500
MIN_QUANTITY = 4
CHECK_INTERVAL = 12 * 60 * 60
TICKPICK_EVENT_URL = "https://www.tickpick.com/buy-don-toliver-tickets-7718028/"
TICKPICK_API_URL = "https://api.tickpick.com/1.0/listings/internal/event-v2/7718028"


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


def send_alert(deal):
    message = (
        f"@everyone DON TOLIVER FLOOR ALERT\n"
        f"Source: {deal['source']}\n"
        f"Section: {deal.get('section', 'N/A')}\n"
        f"Row: {deal['row']}\n"
        f"Price: ${deal['price']}\n"
        f"Quantity: {deal['quantity']}\n"
        f"Buy here: {deal['url']}"
    )
    send_discord(message)
    send_imessage(message)


def check_tickpick():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
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
            page.goto(TICKPICK_EVENT_URL)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

            cookies = context.cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

            data = page.evaluate(f"""
                async () => {{
                    const response = await fetch("{TICKPICK_API_URL}", {{
                        headers: {{
                            "Cookie": "{cookie_str}",
                            "Referer": "https://www.tickpick.com/",
                            "Accept": "application/json"
                        }}
                    }});
                    return response.json();
                }}
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
                            {
                                "source": "TickPick",
                                "section": listing.get("sid"),
                                "row": row,
                                "price": price,
                                "quantity": quantity,
                                "url": TICKPICK_EVENT_URL,
                            }
                        )

            return floor_tickets

        except Exception as e:
            print(f"TickPick error: {e}")
            return []

        finally:
            browser.close()


def run():
    print("Bot started. Checking every 12 hours.")
    while True:
        print("Checking tickets...")
        all_deals = []

        all_deals += check_tickpick()
        all_deals += check_gametime(PRICE_THRESHOLD, MIN_QUANTITY)

        if all_deals:
            cheapest = min(all_deals, key=lambda x: x["price"])
            print(f"Deal found: ${cheapest['price']} on {cheapest['source']}")
            send_alert(cheapest)
        else:
            print(
                f"No floor tickets found with {MIN_QUANTITY}+ quantity under ${PRICE_THRESHOLD}."
            )

        print("Next check in 12 hours.")
        time.sleep(CHECK_INTERVAL)


run()
