import json
import sys
import os
from dotenv import load_dotenv
import argparse
from prompts import system_prompt
from call_function import available_functions, call_function



load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError("The API Key was not found in the .env file.")

from openai import OpenAI

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()
# Now we can access `args.user_prompt`


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": args.user_prompt},
]
for _ in range(20):
    
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools = available_functions
    )


    prompt_tokens = response.usage.prompt_tokens
    response_tokens = response.usage.completion_tokens
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        if prompt_tokens:
            print(f"Prompt tokens: {prompt_tokens}")
        else: 
            raise RuntimeError("Prompt usage property none, possibly failed API request")
        if response_tokens:
            print(f"Response tokens: {response_tokens}")
        else:
            raise RuntimeError("Response tokens not found.")


    message = response.choices[0].message
    messages.append(message)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, args.verbose)
            messages.append(result_message)
            if not result_message["content"]:
                raise Exception("Error:Content is empty")
            if args.verbose:
                print(f"-> {result_message['content']}")
    else:
        print(f"Final response:") 
        print(message.content)
        break
            
else:
    print("All attempts failed.")
    sys.exit(1)
