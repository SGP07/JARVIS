# JARVIS: Personal AI Assistant

## Overview
This project aims to recreate a JARVIS-like AI assistant inspired by Iron Man. The main functionalities include task management, weather information retrieval, internet searches, and maintaining a basic memory system.

## Features
- **To-Do List Management**: Integrated with Todoist for tracking and managing tasks.
- **Weather Reporting**: Real-time weather information retrieval using OpenWeather API.
- **Internet Search**: Perform web searches using Tavily AI.
- **Memory System**: Experimental memory tracking, including potential improvements through Chain of Thought (CoT) prompting.

## Prerequisites
To run this project, you will need to obtain API keys for the following services:
- Groq
- Tavily
- Todoist
- OpenWeather
- Discord

Please ensure that your API keys are stored securely and not exposed in publicly accessible files or repositories.

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SGP07/JARVIS.git
```

### 2. Create Configuration Files

Create a `.env` file in the project root with your API keys:
```
GROQ_API_KEY=""
TAVILY_API_KEY=""
TODOIST_API_TOKEN=""
WEATHER_API_KEY=""  # OpenWeather API Key
DISCORD_TOKEN=""
```

Create a `core_memory.txt` file to store user profile information:
```
Here's what you currently know about the user. Please expand on this as you interact further

Name: Charles Packer
Gender: Male
Occupation: CS student working on an AI project

Notes about their preferred communication style + working habits:
- Wakes up at around 7am.
- Is lazy and always procrastinating.
```

### 3. Install Dependencies
Make sure to install all required dependencies in your environment


### 4. Configure Main Script

Edit the `main.py` file to set up the channel ID for communication with the bot:
```python
# main.py
CHANNEL_ID = 1314631981098864752  # Replace this with your desired channel ID
```

### 5. Run the Assistant
```bash
python main.py
```

## Current Limitations
- The memory system is experimental and may require further development.
- Potential improvements could be made using Chain of Thought (CoT) prompting.
