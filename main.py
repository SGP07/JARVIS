from agent import Agent
from prompts import jarvis_system 
from todoist import fetch_projects, create_project, delete_project,  create_task, close_task, update_task_due_date
from memory import insert_memories, recall_memories, get_core_memory, update_core_memory
from utils import search_web, get_weather, get_tools
from dotenv import load_dotenv
import discord
from discord.ext import commands
import os

load_dotenv()

MODEL = "llama3-groq-70b-8192-tool-use-preview"

jarvis_tools = get_tools()
jarvis_functions = {
        "recall_memories": recall_memories,
        "insert_memories": insert_memories,
        "search_web": search_web,
        "update_core_memory": update_core_memory,
        "get_weather": get_weather,
        "fetch_projects": fetch_projects,
        "create_project": create_project,
        "create_task": create_task,
        "update_task_due_date": update_task_due_date,
        "close_task": close_task,
        "delete_project": delete_project
    }

jarvis = Agent(
    model=MODEL,
    max_tokens=8192,
    temperature=0.8,
    system_prompt=jarvis_system,
    core_memory_path= "core_memory.txt",
    tools=jarvis_tools,
    functions=jarvis_functions
)


CHANNEL_ID = 1314631981098864752 
TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True 
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
    
    if message.channel.id == CHANNEL_ID and not message.content.startswith("!"):
        response = jarvis.run_conversation(message.content)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command()
async def clear(ctx, amount: int = 10):

    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Cleared {amount} messages!", delete_after=2)



bot.run(TOKEN)
