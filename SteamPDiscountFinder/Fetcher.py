import time
import requests

URL = "https://www.cheapshark.com/api/1.0/deals"
HEADERS = {"User-Agent": "SteamDealFinder/1.0 (personal project)"}

def ask(text, default):
    v = input(f"{text} [{default}]: ").strip()
    return float(v) if v else default

def fetch(params, tries=3):
    for i in range(1, tries + 1):
        try:
            r = requests.get(URL, params=params, timeout=40, headers=HEADERS)
            if r.status_code == 200:
                return r.json()
            print("Error:", r.status_code, r.text[:200])
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i}/{tries} failed: {type(e).__name__}")
        if i < tries:
            time.sleep(3)
    print("Could not reach CheapShark. Check your connection/VPN and try again.")
    raise SystemExit

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

deals = [d for d in deals if float(d["savings"]) >= min_discount]
deals.sort(key=lambda d: float(d["salePrice"]))   # cheapest first

print("\n=== DISCOUNTS (cheapest first) ===")
for d in deals:
    print(f"{d['title'][:40]:40} ${float(d['salePrice']):>6.2f} "
          f"-{float(d['savings']):.0f}%")
if not deals:
    print("No deals matched. Try a lower discount or higher max price.")

# ---------- Section 2: 100% off (free to keep) ----------
free = fetch({
    "storeID": 1,
    "upperPrice": 0,
    "onSale": 1,
    "pageSize": 60,
})

free = [d for d in free if float(d["savings"]) >= 99.9]
free.sort(key=lambda d: float(d["normalPrice"]), reverse=True)

print("\n=== FREE TO KEEP (100% off) ===")
for d in free:
    print(f"{d['title'][:40]:40} was ${float(d['normalPrice']):>6.2f}")
    print(f"   https://www.cheapshark.com/redirect?dealID={d['dealID']}")
if not free:
    print("No free-to-keep games right now.")
