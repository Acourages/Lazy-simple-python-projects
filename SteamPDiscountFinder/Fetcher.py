
import time
import requests

URL = "https://www.cheapshark.com/api/1.0/deals"
HEADERS = {"User-Agent": "SteamDealFinder/1.0 (personal project)"}

def ask(text, default):
    while True:
        v = input(f"{text} [{default}]: ").strip()
        if not v:
            return default
        try:
            value = float(v)
            if value < 0:
                print("Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def fetch(params, tries=3):
    for i in range(1, tries + 1):
        try:
            r = requests.get(URL, params=params, timeout=40, headers=HEADERS)
            r.raise_for_status()

            data = r.json()

            if not isinstance(data, list):
                raise ValueError("Unexpected API response format.")

            return data

        except requests.exceptions.Timeout:
            print(f"Attempt {i}/{tries}: Request timed out.")

        except requests.exceptions.ConnectionError:
            print(f"Attempt {i}/{tries}: Connection failed.")

        except requests.exceptions.HTTPError as e:
            print(f"Attempt {i}/{tries}: HTTP Error: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Attempt {i}/{tries}: Request Error: {e}")

        except ValueError as e:
            print(f"Attempt {i}/{tries}: Invalid API response: {e}")

        if i < tries:
            time.sleep(3)

    print("Could not reach CheapShark. Check your connection/VPN and try again.")
    raise SystemExit(1)


# ---------- Section 1: normal discounts ----------
min_discount = ask("Min discount %", 50)
max_price = ask("Max price $", 20)

deals = fetch({
    "storeID": 1,
    "sortBy": "Price",
    "upperPrice": max_price,
    "pageSize": 60,
    "onSale": 1,
})

valid_deals = []

for d in deals:
    try:
        if float(d["savings"]) >= min_discount:
            valid_deals.append(d)
    except (KeyError, TypeError, ValueError):
        continue

deals = valid_deals
deals.sort(key=lambda d: float(d["salePrice"]))   # cheapest first

print("\n=== DISCOUNTS (cheapest first) ===")

for d in deals:
    try:
        print(f"{d['title'][:40]:40} ${float(d['salePrice']):>6.2f} "
              f"-{float(d['savings']):.0f}%")
    except (KeyError, TypeError, ValueError):
        continue

if not deals:
    print("No deals matched. Try a lower discount or higher max price.")


free = fetch({
    "storeID": 1,
    "upperPrice": 0,
    "onSale": 1,
    "pageSize": 60,
})

valid_free = []

for d in free:
    try:
        if float(d["savings"]) >= 99.9:
            valid_free.append(d)
    except (KeyError, TypeError, ValueError):
        continue

free = valid_free
free.sort(key=lambda d: float(d["normalPrice"]), reverse=True)

print("\n=== FREE TO KEEP (100% off) ===")

for d in free:
    try:
        print(f"{d['title'][:40]:40} was ${float(d['normalPrice']):>6.2f}")
        print(f"   https://www.cheapshark.com/redirect?dealID={d['dealID']}")
    except (KeyError, TypeError, ValueError):
        continue

if not free:
    print("No free-to-keep games right now.")
