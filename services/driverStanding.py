from bs4 import BeautifulSoup
import aiohttp
import asyncio
from typing import List, Dict, Any
import json

async def fetch_scoreboard(session: aiohttp.ClientSession, year: str) -> List[Dict[str, Any]]:
    url = f"https://www.formula1.com/en/results/{year}/drivers"
    async with session.get(url) as response:
        if response.status == 200:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', class_='f1-table f1-table-with-data w-full')
            if table:
                rows = table.find_all('tr')[1:]
                scoreboard = []
                for row in rows:
                    cols = row.find_all('td')
                    standing = cols[0].get_text(strip=True)
                    span_driver = cols[1].find_all('span')
                    driver = span_driver[2].get_text(strip=True) + ' ' + span_driver[3].get_text(strip=True)
                    nation = cols[2].get_text(strip=True)
                    team = cols[3].get_text(strip=True)
                    points = cols[4].get_text(strip=True)
                    scoreboard.append({
                        "standing": standing,
                        "driver": driver,
                        "nation": nation,
                        "team": team,
                        "points": points
                    })
                return scoreboard
        return []
    
async def get_scoreboard(year: str) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        return await fetch_scoreboard(session, year)


if __name__ == "__main__":
    async def main():
        async with aiohttp.ClientSession() as session:
            year = "2025"  # Example year, can be parameterized
            scoreboard = await fetch_scoreboard(session, year)
            # print(scoreboard)
            with open('temp.json', 'w') as f:
                json.dump(scoreboard, f, indent=4)
            
    asyncio.run(main())