import discord
import dotenv
import os
from discord.ext import commands
from services.formulanews import get_latest_news
from services.formulasessions import get_session_data
import asyncio
from typing import cast

dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN')
NEWS_CHANNEL_ID = os.getenv('NEWS_CHANNEL_ID')

if not TOKEN:
    raise ValueError("TOKEN environment variable is required")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

last_news = []

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    client.loop.create_task(news_update())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello! World!')

    if message.content.startswith('$news'):
        global last_news
        news = await get_latest_news()
        title = news[0]['title']
        href = news[0]['href']
        await message.channel.send(f'Latest News: {title}\nRead more: https://www.formula1.com{href}')     
        last_news = news
    if message.content.startswith('$sessions'):
        location = message.content.split('$sessions ')[1].strip()
        if not location:
            await message.channel.send('Please provide race location.')
        else:
            info = await get_session_data(location)
            if info:
                response = f"🏎️ **F1 Sessions for {location.title()}** 🏎️\n\n"
                
                for session in info:
                    session_id = session.get('session_id', 'Unknown')
                    date = session.get('date', '')
                    month = session.get('month', '')
                    time = session.get('time', '')
                    status = session.get('status', 'Unknown')
                    results = session.get('results', [])
                    
                    if status == "Not Finished":
                        status_emoji = "🔜"
                    else:
                        status_emoji = "✅"
                    
                    response += f"{status_emoji} **{session_id}**\n"
                    response += f"📅 {date} {month} at {time}\n"
                    response += f"📊 Status: {status}\n"
                    
                    if results:
                        response += "🏆 **Top Results:**\n"
                        for result in results[:3]:  # Show top 3
                            pos = result.get('position', '')
                            driver = result.get('driver', '')
                            team = result.get('team', '')
                            time_or_laps = result.get('time_or_laps', result.get('time', ''))
                            response += f"  {pos}. {driver} ({team}) - {time_or_laps}\n"
                    
                    response += "\n"
                
                if len(response) > 1900:
                    chunks = []
                    current_chunk = f"🏎️ **F1 Sessions for {location.title()}** 🏎️\n\n"
                    
                    for session in info:
                        session_text = ""
                        session_id = session.get('session_id', 'Unknown')
                        date = session.get('date', '')
                        month = session.get('month', '')
                        time = session.get('time', '')
                        status = session.get('status', 'Unknown')
                        results = session.get('results', [])
                        
                        if status == "Not Finished":
                            status_emoji = "🔜"
                        else:
                            status_emoji = "✅"
                        
                        session_text += f"{status_emoji} **{session_id}**\n"
                        session_text += f"📅 {date} {month} at {time}\n"
                        session_text += f"📊 Status: {status}\n"
                        
                        if results:
                            session_text += "🏆 **Top Results:**\n"
                            for result in results[:3]:
                                pos = result.get('position', '')
                                driver = result.get('driver', '')
                                team = result.get('team', '')
                                time_or_laps = result.get('time_or_laps', result.get('time', ''))
                                session_text += f"  {pos}. {driver} ({team}) - {time_or_laps}\n"
                        
                        session_text += "\n"
                        
                        if len(current_chunk + session_text) > 1900:
                            chunks.append(current_chunk)
                            current_chunk = session_text
                        else:
                            current_chunk += session_text
                    
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
            else:
                await message.channel.send(f"❌ No session data found for '{location}'. Please check the location name.")

    if message.content.startswith('$wdc'):
        year = message.content.split('$wdc ')[1].strip()
        if not year:
            await message.channel.send('Please provide a year.')
        else:
            try:
                from services.formuladriverStanding import get_scoreboard
                scoreboard = await get_scoreboard(year)
                if scoreboard:
                    response = f"WDC {year}:\n\n"
                    for entry in scoreboard:
                        response += f"{entry['standing']}. {entry['driver']} ({entry['team']}) - {entry['points']} pts\n"
                    await message.channel.send(response)
                else:
                    await message.channel.send(f"No data found for WDC {year}.")
            except Exception as e:
                await message.channel.send(f"Error fetching WDC data: {e}")
        

async def news_update():
    global last_news
    await client.wait_until_ready()
    
    if not NEWS_CHANNEL_ID:
        print("NEWS_CHANNEL_ID not configured, skipping news updates")
        return
        
    channel = client.get_channel(int(NEWS_CHANNEL_ID))
    if not channel:
        print(f"Channel not found: {NEWS_CHANNEL_ID}")
        return
    
    # Type cast to TextChannel for proper typing
    text_channel = cast(discord.TextChannel, channel)
    
    while not client.is_closed():
        try:
            news = await get_latest_news()
            if news and news != last_news:
                title = news[0]['title']
                href = news[0]['href']
                await text_channel.send(f'Latest News: {title}\nRead more: https://www.formula1.com{href}')
                last_news = news
        except Exception as e:
            print(f"Error in news update: {e}")
        await asyncio.sleep(3600)


client.run(TOKEN)