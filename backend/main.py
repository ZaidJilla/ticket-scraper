from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

active_jobs = {}


class MonitorConfig(BaseModel):
    eventId: str
    eventName: str
    venue: str
    city: str
    state: str
    date: str
    priceThreshold: float
    minQuantity: int
    webhook: str
    mention: str


def send_discord(webhook, message):
    requests.post(webhook, json={"content": message})


def check_gametime(event_id, price_threshold, min_quantity):
    url = f"https://mobile.gametime.co/v3/listings/{event_id}?all_in_pricing=true&quantity={min_quantity}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = response.json()
    floor_tickets = []
    for listing in data.get("listings", []):
        spot = listing.get("spot", {})
        if spot.get("section_group") == "Floor":
            price = listing.get("price", {}).get("total", 0) / 100
            quantity = len(listing.get("available_lots", []))
            if price <= price_threshold and quantity >= min_quantity:
                floor_tickets.append(
                    {
                        "price": price,
                        "row": spot.get("row"),
                        "section": spot.get("section"),
                        "quantity": quantity,
                    }
                )
    return floor_tickets


def monitor_job(config: MonitorConfig):
    while active_jobs.get(config.eventId):
        print(f"Checking {config.eventName}...")
        deals = check_gametime(
            config.eventId, config.priceThreshold, config.minQuantity
        )
        print(f"Found {len(deals)} deals")
        if deals:
            cheapest = min(deals, key=lambda x: x["price"])
            message = (
                f"{config.mention} FLOOR TICKET ALERT\n"
                f"Event: {config.eventName}\n"
                f"Venue: {config.venue} · {config.city}, {config.state}\n"
                f"Row: {cheapest['row']} | Section: {cheapest['section']}\n"
                f"Price: ${cheapest['price']}\n"
                f"Quantity: {cheapest['quantity']}\n"
                f"Buy here: https://gametime.co/events/{config.eventId}"
            )
            send_discord(config.webhook, message)
            print("Alert sent!")
        time.sleep(2 * 60 * 60)


@app.post("/api/monitor")
def start_monitor(config: MonitorConfig):
    if config.eventId in active_jobs:
        return {"status": "already running"}
    active_jobs[config.eventId] = True
    thread = threading.Thread(target=monitor_job, args=(config,), daemon=True)
    thread.start()
    return {"status": "started", "eventId": config.eventId}


@app.get("/api/jobs")
def get_jobs():
    return {"jobs": list(active_jobs.keys())}


@app.delete("/api/jobs/{event_id}")
def stop_job(event_id: str):
    active_jobs.pop(event_id, None)
    return {"status": "stopped"}
