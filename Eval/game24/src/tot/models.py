import os
import openai
import backoff 
import pdb
import sys
from .argparser import parse_args
args = parse_args()
completion_tokens = prompt_tokens = 0
"""
api_key = os.getenv("OPENAI_API_KEY", "")
if api_key != "":
    openai.api_key = api_key
else:
    print("Warning: OPENAI_API_KEY is not set")
    
api_base = os.getenv("OPENAI_API_BASE", "")
if api_base != "":
    print("Warning: OPENAI_API_BASE is set to {}".format(api_base))
    openai.api_base = api_base

@backoff.on_exception(backoff.expo, openai.error.OpenAIError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)
"""

prompt_llama = '''<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

{USER_INPUT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
'''

client = None

def completions_with_backoff_debug(**kwargs):
    from openai import OpenAI
    global client
    if not client:
        client = OpenAI(
            #base_url="http://172.30.150.32:7777/v1",
            #base_url="http://9.33.169.151:7779/v1",
            base_url=args.llm_api,
            api_key="token-abc123",
        )
    processed_input = kwargs["messages"][0]["content"]
    use_llama_prompt = False
    if use_llama_prompt:
        processed_input = prompt_llama.format(USER_INPUT=processed_input)
    kwargs["messages"][0]["content"] = processed_input 
    kwargs["model"] = args.backend 
    output =  client.chat.completions.create(**kwargs)
    #print(processed_input)
    #print(output.choices[0].message.content)
    #pdb.set_trace()
    return output

def gpt(prompt, model="gpt-4", temperature=0.7, max_tokens=150, n=1, stop=None) -> list:
    messages = [{"role": "user", "content": prompt}]
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)
    
def chatgpt(messages, model="gpt-5", temperature=0.7, max_tokens=150, n=1, stop=None) -> list:
    global completion_tokens, prompt_tokens
    outputs = []
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = completions_with_backoff_debug(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
        #outputs.extend([choice["message"]["content"] for choice in res["choices"]])
        outputs.extend([choice.message.content for choice in res.choices])
        # log completion tokens
        #completion_tokens += res["usage"]["completion_tokens"]
        completion_tokens += res.usage.completion_tokens
        #prompt_tokens += res["usage"]["prompt_tokens"]
        prompt_tokens += res.usage.prompt_tokens
    return outputs
    
def gpt_usage(backend="gpt-4"):
    global completion_tokens, prompt_tokens
    if backend == "gpt-4":
        cost = completion_tokens / 1000 * 0.06 + prompt_tokens / 1000 * 0.03
    elif backend == "gpt-3.5-turbo":
        cost = completion_tokens / 1000 * 0.002 + prompt_tokens / 1000 * 0.0015
    else:
        cost = 0
    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
