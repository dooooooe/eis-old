import discord
import eis
import dooe
import dotenv
import os

# setup
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# startup
@client.event
async def on_ready():
    print(f"{client.user.name}: hiii :3\n")
    await eis.startup(client)

# run
@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith(PREFIX):
        await eis.process(client, message)

    if message.content.startswith('eis ') and message.author.id == 326435590666977280:
        await dooe.process(client, message)


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == client.user and user != client.user:
        await reaction.message.remove_reaction(str(reaction.emoji), user)
    
    
client.run(TOKEN)