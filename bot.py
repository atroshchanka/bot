import os
import discord
import requests
import asyncio


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
STEAM_KEY = os.getenv("STEAM_KEY")
APP_ID = "1304930"  # The Outlast Trials

CHANNEL_ID = os.getenv("CHANNEL_ID")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

def get_players():
    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={APP_ID}&key={STEAM_KEY}"
        r = requests.get(url).json()
        return r["response"]["player_count"]
    except Exception as e:
        print(f"Ошибка получения игроков: {e}")
        return 0

async def update_channel_name():
    await bot.wait_until_ready()
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
    except Exception as e:
        print(f"Не удалось получить канал: {e}")
        return

    last_count = None
    threshold = 100

    while not bot.is_closed():
        count = get_players()
        if last_count is None or abs(count - last_count) > threshold:  # обновляем только если число изменилось
            new_name = f"🌐 Онлайн в игре: {count:,}"
            try:
                await channel.edit(name=new_name)
                print(f"[{discord.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Название канала обновлено: {new_name}")
                last_count = count
            except discord.Forbidden:
                print("Нет прав на изменение канала!")
            except discord.HTTPException as e:
                print(f"Ошибка при редактировании: {e}")
        await asyncio.sleep(180)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    bot.loop.create_task(update_channel_name())

bot.run(DISCORD_TOKEN)
