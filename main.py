from todoist import fetch_projects, create_project, delete_project,  create_task, close_task, update_task_due_date, get_todo_tools
from memory import insert_memories, recall_memories, get_core_memory, update_core_memory, get_memory_tools
from utils import get_search_tool, search_web, get_weather, get_datetime, get_agent_tools
from dotenv import load_dotenv
from prompts import jarvis_system, utility_system, todo_system
from agent import Agent
from discord.ext import commands
import discord
import os

load_dotenv()

MODEL = "llama3-groq-70b-8192-tool-use-preview"

todo_agent = Agent(
    name="todo", 
    model=MODEL,
    max_tokens=4096,
    temperature=0,
    system_prompt=f"{todo_system}\nCurrent date and time: {get_datetime()}\nUse this date for any time-sensitive queries or date-specific requests",
    tools = get_todo_tools(),
    functions=  {      
        "fetch_projects": fetch_projects,
        "create_project": create_project,
        "create_task": create_task,
        "update_task_due_date": update_task_due_date,
        "close_task": close_task,
        "delete_project": delete_project
        },
    maintain_history=True
)

utility_agent = Agent(
    name="utility", 
    model=MODEL,
    max_tokens=4096,
    temperature=0,
    system_prompt=f"{utility_system}\nCurrent date and time: {get_datetime()}",
    tools = get_search_tool(),
    functions= {
        "search_web": search_web,
        "get_weather": get_weather,
        }
)

jarvis_tools = get_memory_tools() + get_agent_tools()


jarvis = Agent(
    name="jarvis", 
    model=MODEL,
    max_tokens=8192,
    temperature=0.8,
    system_prompt=f"{jarvis_system} \n{get_core_memory()}\nCurrent date and time: {get_datetime()}",
    tools=jarvis_tools,
    functions={
        "recall_memories": recall_memories,
        "insert_memories": insert_memories, 
        "update_core_memory": update_core_memory,
        "utility_manager": utility_agent.run_conversation,
        "todolist_manager": todo_agent.run_conversation,
    },
    maintain_history=True
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
