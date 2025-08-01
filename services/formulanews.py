from bs4 import BeautifulSoup
import aiohttp
import asyncio
from typing import List, Dict, Any
import json

URL = "https://www.formula1.com/en/latest"

async def fetch_news(session: aiohttp.ClientSession) -> Dict[str, Any]:
    title = []
    href = []
    async with session.get(URL) as response:
        if response.status == 200:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            grid = soup.find('ul', class_='grid md:grid-cols-2 gap-px-16 lg:gap-px-24')
            if grid:
                list_items = grid.find_all('li')[:3]
                for item in list_items:
                    title.append(item.find('a').get_text())
                    href.append(item.find_next('a')['href'])

    return {
        "title": title,
        "href": href
    }

async def update_news():
    async with aiohttp.ClientSession() as session:
        result = await fetch_news(session)
        news = {
            "title": result["title"],
            "href": result["href"]
        }

        with open('db/news.json', 'w') as f:
            json.dump(news, f, indent=4)

async def get_latest_news() -> List[Dict[str, str]]:
    await update_news()
    with open('db/news.json', 'r') as f:
        result = json.load(f)
        if not result:
            await update_news()
            f.seek(0)
            result = json.load(f)
    return [{"title": result["title"][0], "href": result["href"][0]}]

async def main():
    await update_news()
    news = await get_latest_news()
    for item in news:
        print(item['title'])
        print(item['href'])
        print('---')

if __name__ == "__main__":
    asyncio.run(main())