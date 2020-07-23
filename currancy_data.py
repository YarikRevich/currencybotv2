import requests
import asyncio
from datetime import datetime

from db import DB

data = DB()

async def get_data():
    r = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
    while True:
        await asyncio.sleep(3000)
        
        await data.write_currant_currency(
            (str(r.json()[33]["cc"]),str(r.json()[26]["cc"])),
            (str(r.json()[33]["rate"]),str(r.json()[26]["rate"])),
            (datetime.today().strftime("%Y-%m-%d"),datetime.today().strftime("%Y-%m-%d")),
            )
        
