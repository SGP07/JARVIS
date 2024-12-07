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

def summarize_content(search_results):
    

    chat_completion = client.chat.completions.create(
    messages = [
    {
        "role": "system",
        "content": "You are a search results condensation assistant. Summarize each search result in 2-3 sentences while keeping the exact original format: 'Number. Title: {title}\nURL: {url}\nContent: {condensed_content}'. Preserve the full title and URL, and distill the content to its most essential information, capturing the key points concisely."
    },
    {
        "role": "user",
        "content": f"Provide a concise summary of these search results:\n{search_results}"
    }
],
    model="llama3-8b-8192",
)

    return chat_completion.choices[0].message.content

def process_response(response, num_results=4):
    search_results = ""
    for i in range(num_results):
        search_results += f"{i+1}. Title: {response[i]['title']}\nURL: {response[i]['url']}\nContent: {response[i]['content'].strip()}\n\n"

    return search_results


def search_web(query: str, num_results=4):
    print(f"\n###Searching for : {query}")
    response = tavily_client.search(query)

    results = process_response(response["results"], num_results)
    # smry_rslt = summarize_content(results)
    smry_rslt = results

    print(f"\n*Results*:\n{smry_rslt}\n")
    return smry_rslt

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


def get_tools():
    return [
         {
        "type": "function",
        "function": {
            "name": "recall_memories",
            "description": "Retrieve relevant memories based on a given query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A text query to search and retrieve relevant memories"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "The maximum number of memory results to return (optional, defaults to 3)",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    },
        {
            "type": "function",
            "function": {
                "name": "insert_memories",
                "description": "Insert one or multiple memories into the collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "memories": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "A list of memory contents to be inserted. Can be a single memory or multiple memories."
                        }
                    },
                    "required": ["memories"]
                }
            }
        },
        
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
                "name": "update_core_memory", 
                "description": "Appends a new line to the core memory ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "new_line": {
                            "type": "string",
                            "description": "The new line of text to append to the core memory "
                        }
                    },
                    "required": ["new_line"]
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
        {
            "type": "function",
            "function": {
                "name": "fetch_projects",
                "description": "Retrieve all projects and their associated tasks from Todoist",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_project",
                "description": "Create a new project in Todoist",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the new project to be created"
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task in a specific Todoist project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name/content of the task"
                        },
                        "project_id": {
                            "type": "integer",
                            "description": "ID of the project to which the task belongs"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the task"
                        },
                        "due_string": {
                            "type": "string",
                            "description": "Optional due date/time for the task (e.g., 'tomorrow', '2024-12-31')"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Optional priority of the task (1-4)"
                        }
                    },
                    "required": ["name", "project_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task_due_date",
                "description": "Update the due date of an existing task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "due_string": {
                            "type": "string",
                            "description": "New due date/time for the task (e.g., 'tomorrow', '2024-12-31')"
                        }
                    },
                    "required": ["task_id", "due_string"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "close_task",
                "description": "Mark a specific task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to close/complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_project",
                "description": "Delete a specific project from Todoist",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "integer",
                            "description": "ID of the project to be deleted"
                        }
                    },
                    "required": ["project_id"]
                }
            }
        }
    ]
