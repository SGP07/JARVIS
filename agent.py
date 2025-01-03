from memory import get_core_memory
from utils import get_datetime
from prompts import jarvis_system
from groq import Groq
from dotenv import load_dotenv
from cprint import cprint
import os
import json

load_dotenv()

class Agent:
    def __init__(self, name, model, max_tokens, temperature, system_prompt, tools, functions, maintain_history=False):
        self.name = name
        self.model = model
        self.max_tokens = max_tokens
        self.tools = tools
        self.functions = functions
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.maintain_history = maintain_history
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            )
        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        print(f"\n\n-----init {self.name}-----\n{self.system_prompt}\n\n\n")


    def run_conversation(self, user_prompt):
        if not self.maintain_history:
            self.messages = [
                {"role": "system", "content": self.system_prompt}
            ]

        self.messages.append({"role": "user", "content": user_prompt})
        
        response = self.chat_completion()
        while tool_calls := response.tool_calls:

            self.process_tool_calls(tool_calls)
            response = self.chat_completion()
        else:
            final_response = response
        
        print(f"\n{self.name}: {final_response}\n")
        return final_response.content
    
    def chat_completion(self):
        cprint(self.messages[-1])
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
        print(f"{self.name} tool calls: {tool_calls}\n")
        for tool_call in tool_calls:
            print(f"----------------\n\n{tool_call}\n\n----------------")
            function_name = tool_call.function.name
            function_to_call = self.functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            try:
                function_response = function_to_call(**function_args)
                print(f"\nresponse:\n{function_response}\n")
            except Exception as e:
                function_response = {"error": str(e)}
                print(f"\nError in function {function_name}: {function_response}\n")
            

            print(f"\nresponse:\n{function_response}\n")
            if function_name == "update_core_memory":
                self.update_system_prompt(f"{jarvis_system} \n{get_core_memory()}\nCurrent date and time: {get_datetime()}")

            self.messages.append({
            "tool_call_id": tool_call.id, 
            "role": "tool",
            "name": function_name,
            "content": str(function_response),
        })

    def update_system_prompt(self, new_system_prompt):
        self.messages[0] = [
            {
                "role": "system",
                "content": new_system_prompt
            }
        ]
        print(f"\n\nSYSTEM PROMPT UPDATE\n{new_system_prompt}\n\n")
        