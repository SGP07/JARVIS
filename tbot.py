from todoist import fetch_projects, create_project, delete_project,  create_task, close_task, update_task_due_date, get_todo_tools
from prompts import jarvis_system, utility_system, todo_system
from memory import insert_memories, recall_memories, get_core_memory, core_memory_append, core_memory_replace, get_memory_tools
from utils import get_search_tool, search_web, get_weather, get_datetime, get_agent_tools
from agent import Agent

from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs

import telebot
from telebot.types import InputFile

from dotenv import load_dotenv
import os

import time
import base64

from groq import Groq


load_dotenv()


client = Groq(
	api_key=os.environ.get("GROQ_API_KEY"),
)

vclient = ElevenLabs(
  api_key=os.environ.get("ELEVENLABS_API_KEY"),
)

def generate_audio(text):
	output = "voicemsgs/jarvis_reply.mp3"
	audio = vclient.generate(
    text=text,
    voice=Voice(
        voice_id='Slz67floc4rQHMAxiqdo', #replace with your voiceid
        settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
    )
)
	save(audio, output)
	return output
	


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def transcribe_voice(audio_file):
	with open(audio_file, "rb") as file:
		# Create a transcription of the audio file
		transcription = client.audio.transcriptions.create(
		file=(audio_file, file.read()), # Required audio file
		model="whisper-large-v3-turbo", # Required model to use for transcription
		)
		# Print the transcription text
		print(transcription.text)
		return transcription.text

def describe_img(base64_image):
	completion = client.chat.completions.create(
		model="llama-3.2-11b-vision-preview",
		messages= [
	        {
				"role": "user",
				"content":
					[
						{
							"type": "text",
							"text":"provide an accurate and detailed description of the image"},
						{
							"type": "image_url",
							"image_url": {
								"url": f"data:image/jpeg;base64,{base64_image}",
							}
						}

					]
				}
			],
		temperature=1,
		max_tokens=1024,
		top_p=1,
		stream=False,
		stop=None,
		)

	return completion.choices[0].message
	
MODEL = "llama-3.3-70b-versatile"
# MODEL = "llama3-groq-70b-8192-tool-use-preview"

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
    system_prompt=f"{jarvis_system}\n{get_core_memory()}\nCurrent date and time: {get_datetime()}",
    tools=jarvis_tools,
    functions={
        "recall_memories": recall_memories,
        "insert_memories": insert_memories, 
        "core_memory_append": core_memory_append,
        "core_memory_replace": core_memory_replace,
        "utility_manager": utility_agent.run_conversation,
        "todolist_manager": todo_agent.run_conversation,
    },
    maintain_history=True
)


TOKEN = os.environ.get("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi there, I am Jarvis.")



@bot.message_handler(content_types=['text', 'photo', 'voice'])
def reply_to_message(message):
	print(message, end="\n\n")
    
	text_content = None
	image_content = None

	if message.text:
		text_content = message.text
	
	print("test")

	if message.photo:
		print("has a photo")
		try:
			# Get the photo with the highest quality
			file_info = bot.get_file(message.photo[-1].file_id)
			
			# Generate unique filename using timestamp
			filename = f"imgs/image_{int(time.time())}.jpg"
			
			# Download and save the file
			downloaded_file = bot.download_file(file_info.file_path)
			with open(filename, 'wb') as new_file:
				new_file.write(downloaded_file)
			
			# Store the path
			image_content = filename
			
			# If there's a caption, use it as text_content
			if message.caption:
				text_content = message.caption
				
		except Exception as e:
			bot.reply_to(message, f"Sorry, I couldn't process that image: {str(e)}")
			return

	print("made it here")

	if message.voice:
		print("voice")
		file_info = bot.get_file(message.voice.file_id)
		filename = f"C:/Users/MSI/Documents/Dev/Jarvis/voicemsgs/voice_{int(time.time())}.ogg"
		downloaded_file = bot.download_file(file_info.file_path)
		with open(filename, 'wb') as new_file:
			new_file.write(downloaded_file)

		voice_content = transcribe_voice(filename)
		response = jarvis.run_conversation(voice_content)
		voice_reply = generate_audio(response)

		print(voice_reply)
		
		bot.send_voice(chat_id=message.chat.id, voice=InputFile(voice_reply), caption=response)
		return


	if not image_content:	
		print("no image")	
		response = jarvis.run_conversation(text_content)
		bot.reply_to(message, response)
		return
	
	else:
		print("img")
		base64_image = encode_image(image_content)
				
		img_description = describe_img(base64_image)
		response = jarvis.run_conversation(f"{text_content}\n### the user included an image, here's a detailed description :\n{img_description}")
		bot.reply_to(message, response)
		return


bot.infinity_polling()