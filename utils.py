from tavily import TavilyClient
from dotenv import load_dotenv
from datetime import datetime
from groq import Groq
import requests
import os

load_dotenv()

tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def process_response(response, num_results=4):
    search_results = ""
    for i in range(num_results):
        search_results += f"{i+1}. Title: {response[i]['title']}\nURL: {response[i]['url']}\nContent: {response[i]['content'].strip()}\n\n"

    return search_results


def search_web(query: str, num_results=4):
    print(f"\n###Searching for : {query}, num results: {num_results}")
    response = tavily_client.search(query)

    results = process_response(response["results"], num_results)

    print(f"\n*Results*:\n{results}\n")
    return results

def get_weather(location):
    print(f"\n\nrequesting weather in {location}")
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    
    params = {
        'q': location,
        'appid': WEATHER_API_KEY,
        'units': 'metric' 
    }
    
    try:
        response = requests.get(BASE_URL, params=params)

        response.raise_for_status()

        weather_data = response.json()
        weather_info = {
            'location': weather_data['name'],
            'country': weather_data['sys']['country'],
            'temperature': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description'],
            'wind_speed': weather_data['wind']['speed']
        }

        print(f"###GET WEATHER:\n{weather_info}")

        return weather_info
    
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_datetime():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def get_search_tool():
    return [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Perform a web search based on a given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to perform"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "The number of search results to return (optional, defaults to 4)",
                            "default": 4
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Retrieves current weather information for a specified location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or city,country code (e.g., 'Rabat')",
                            "examples": [
                                "Agadir",
                                "Paris,FR", 
                                "Tokyo,JP",
                                "Sydney,AU"
                            ]
                        }
                    },
                    "required": ["location"]
                }
            }
        },
    ]

def get_agent_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "utility_manager",
                "description": "Manages and responds to utility-related queries or tasks using natural language processing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_prompt": {
                            "type": "string",
                            "description": "Natural language prompt describing a utility-related task or query",
                            "examples": [
                                "Calculate my electricity bill for this month",
                                "Help me understand my water usage",
                                "Schedule a maintenance check for my home utilities",
                                "Compare electricity providers in my area"
                            ]
                        }
                    },
                    "required": ["user_prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "todolist_manager",
                "description": "Manages todo lists through natural language interactions, including adding, removing, updating, and organizing tasks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_prompt": {
                            "type": "string",
                            "description": "Natural language prompt for managing todo list tasks",
                            "examples": [
                                "Add a new task to buy groceries this weekend",
                                "List all my current tasks",
                                "Mark the project report task as complete",
                                "Remove the gym appointment from my todo list",
                                "Prioritize my tasks for this week"
                            ]
                        }
                    },
                    "required": ["user_prompt"]
                }
            }
        }
    ]