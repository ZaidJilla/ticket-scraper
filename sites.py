import requests

GAMETIME_API = "https://mobile.gametime.co/v3/listings/69822505d77ef776ec541b56?all_in_pricing=true&quantity=4&jitter_cheapest=0"
GAMETIME_EVENT_URL = "https://gametime.co/concert/don-toliver-tickets/5-30-2026-boston-ma-td-garden/events/69822505d77ef776ec541b56"


def check_gametime(price_threshold, min_quantity):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(GAMETIME_API, headers=headers)
        data = response.json()
        listings = data["listings"]
        floor_tickets = []

        for listing in listings:
            spot = listing.get("spot", {})
            section_group = spot.get("section_group", "")
            price_cents = listing.get("price", {}).get("total", 0)
            price = price_cents / 100
            quantity = len(listing.get("available_lots", []))
            row = spot.get("row")
            section = spot.get("section")

            if (
                section_group == "Floor"
                and price <= price_threshold
                and quantity >= min_quantity
            ):
                floor_tickets.append(
                    {
                        "source": "Gametime",
                        "section": section,
                        "row": row,
                        "price": price,
                        "quantity": quantity,
                        "url": GAMETIME_EVENT_URL,
                    }
                )

        return floor_tickets

    except Exception as e:
        print(f"Gametime error: {e}")
        return []
