from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

async def fetch_binance_usdt_rate():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "asset": "USDT",
            "fiat": "NGN",
            "page": 1,
            "rows": 1,
            "tradeType": "BUY"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()
            rate = float(data['data'][0]['adv']['price'])
            return rate
    except:
        return None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    binance_rate = await fetch_binance_usdt_rate()
    if binance_rate:
        platforms = {
            "Binance P2P": binance_rate,
            "KuCoin": binance_rate + 30,  # just simulate
            "Bundle": binance_rate - 25,  # simulate
        }

        # Calculate arbitrage
        buy_from = min(platforms, key=platforms.get)
        sell_to = max(platforms, key=platforms.get)
        profit = platforms[sell_to] - platforms[buy_from]

        return templates.TemplateResponse("index.html", {
            "request": request,
            "platforms": platforms,
            "buy_from": buy_from,
            "sell_to": sell_to,
            "profit": round(profit, 2)
        })
    else:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Unable to fetch data at the moment"
        })
      
