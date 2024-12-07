from groq import Groq
from dotenv import load_dotenv
import os
import json
from utils import get_datetime
from memory import get_core_memory, update_core_memory

load_dotenv()

class Agent:
    def __init__(self, model, max_tokens, temperature, system_prompt, core_memory_path, tools, functions):
        self.model = model
        self.max_tokens = max_tokens
        self.tools = tools
        self.functions = functions
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.core_memory = get_core_memory(core_memory_path)
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            )
        self.messages = [
            {
                "role": "system",
                "content": f"{system_prompt} \n{self.core_memory}\nCurrent date and time: {get_datetime()}"
            }
        ]


    def run_conversation(self, user_prompt):
        self.messages.append({"role": "user", "content": user_prompt})
        
        response = self.chat_completion()
        tool_calls = response.tool_calls
        if tool_calls:
            self.process_tool_calls(tool_calls)

            final_response = self.chat_completion()
        else:
            final_response = response
        
        return final_response.content
    
    def chat_completion(self):
        response = self.client.chat.completions.create(
        model = self.model,
        messages = self.messages,
        stream= False,
        tools = self.tools,
        tool_choice = "auto",
        max_tokens = self.max_tokens,
        temperature= self.temperature
    )
        response_message = response.choices[0].message
        self.messages.append(response_message)

        return response_message
    
    def process_tool_calls(self, tool_calls):
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = self.functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            function_response = function_to_call(**function_args)
            if function_name == "update_core_memory":
                self.core_memory = get_core_memory()
                self.update_system()

            self.messages.append({
            "tool_call_id": tool_call.id, 
            "role": "tool",
            "name": function_name,
            "content": str(function_response),
        })

    def update_system(self):
        self.messages[0] = [
            {
                "role": "system",
                "content": f"{self.system_prompt} \n{self.core_memory}\nCurrent date and time: {get_datetime()}"
            }
        ]
    
        