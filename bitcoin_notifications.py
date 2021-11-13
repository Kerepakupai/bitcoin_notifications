import requests
import time
from datetime import datetime

BITCOIN_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
IFTTT_WEBHOOKS_URL = "https://maker.ifttt.com/trigger/{}/json/with/key/bTefwmN3gmAgAW-tWdZwPH"
BITCOIN_PRICE_THRESHOLD = 65000

def get_latest_bitcoin_price():
    params = {
        'start':'1',
        'limit':'2',
        'convert':'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'd40996de-399b-4a17-84e9-14701a7515c7',
    }
    response = requests.get(BITCOIN_API_URL, params=params, headers=headers)
    response_json = response.json()
    # Convert the price to a floating point number
    return round(float(response_json["data"][0]["quote"]["USD"]["price"]), 2)


def post_ifttt_webhook(event, value):
    # The payload that will be sent to IFTTT service
    data = {"value1": value}
    # Inserts our desired event
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)


def format_bitcoin_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        # Formats the date into a string "24.02.2018 15:09"
        date = bitcoin_price["date"].strftime("%d.%m.%Y %H:%M")
        price = bitcoin_price["price"]
        row = "{}: $<b>{}</b>".format(date, price)
        rows.append(row)
    
    # Use a <br> (break) tag to create a new line
    # Join the rows delimited by <br> tag: row1<br>row2<br>row3
    return "<br>".join(rows)


def main():
    bitcoin_history = []
    while True:
        price = get_latest_bitcoin_price()
        date = datetime.now()
        bitcoin_history.append({"date": date, "price": price})
        print(f"date: {date} - price: {price}")

        # Send an emergency notification
        if price < BITCOIN_PRICE_THRESHOLD:
            post_ifttt_webhook("bitcoin_price_emergency", price)

        # Send a Telegram notification
        # Once we have 5 items in our bitcoin_history send an update
        if len(bitcoin_history) == 5:
            post_ifttt_webhook("bitcoin_price_update", format_bitcoin_history(bitcoin_history))
            # Reset the history
            bitcoin_history = []
        
        # Sleep for 5 minutes
        time.sleep(1 * 60)


if __name__ == "__main__":
    main()