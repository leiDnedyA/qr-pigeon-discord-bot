import discord
import requests
import asyncio
import subprocess
import os
import getpass
import sys

# Configuration
discord_token = "MTIzMTQ1ODA3ODc1MTQ2MTQ0OQ.GbnC6x.njc2P7NXRoCmee743sDSH-R5uy35dfOjBWxJAE"
status_channel_name = "status"
website_url = "https://www.qrpigeon.pics"
check_interval = 900 # 15 minutes (900 seconds)

if len(sys.argv) < 2:
    print("Incorrect usage, call script as follows:\
            'python3 bot.py <sudo password>'")
    exit()

sudo_password = sys.argv[1]

# Commands to run if the specified reaction is added
def run_commands():
    # If gunicorn is not running, start it
    gunicorn_running = False
    p = subprocess.run(['ps', '-d'], text=True, stdout=subprocess.PIPE)
    if p.returncode == 0:
        nginx_check = 'gunicorn' in p.stdout
    if not gunicorn_running:
        os.chdir('/home/ayden/qr-image-drop')
        commands = [
            "pwd",
            f"echo '{sudo_password}' | sudo -S bash prod.sh"
        ]
        for command in commands:
            os.system(command)

    # If nginx is not running, start it
    nginx_running = False
    p = subprocess.run(['ps', '-d'], text=True, stdout=subprocess.PIPE)
    if p.returncode == 0:
        nginx_check = 'nginx' in p.stdout
    if not nginx_running:
        os.chdir('/home/ayden/nginx_config')
        commands = [
            "pwd",
            f"echo '{sudo_password}' | sudo -S bash start.sh"
        ]
        for command in commands:
            os.system(command)

# Bot setup with intent to capture reactions
intents = discord.Intents.default()
intents.reactions = True  # Allow the bot to listen to reactions
intents.messages = True  # Allow the bot to send messages

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")

    # Function to check the website's status
    async def check_website():
        channel = discord.utils.get(client.guilds[1].channels, name=status_channel_name)
        while True:
            try:
                response = requests.get(website_url, timeout=10, verify=False)
                if response.status_code != 200:
                    # Send a message when the website is down
                    bot_message = await channel.send(
                        "@everyone QR Pigeon is down. React with 👍 to bring it back up."
                    )
                await asyncio.sleep(check_interval)
            except requests.RequestException:
                await channel.send("@everyone QR Pigeon is down.")

    # Start checking the website in the background
    client.loop.create_task(check_website())

@client.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji)
    # If the reaction is a 'like' emoji and the message is from the bot
    if reaction.emoji == '👍' and reaction.message.author == client.user:
        await reaction.message.channel.send("Executing commands to bring the site back up...")
        run_commands()

# Start the bot
client.run(discord_token)
