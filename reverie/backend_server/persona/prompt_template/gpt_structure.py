"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling the OpenAI API.

This is the `openai-backend` branch: a drop-in replacement for the original
Ollama/Gemma wiring that uses OpenAI's hosted models end-to-end.

  chat completions  → gpt-4o-mini
  embeddings        → text-embedding-3-small

Set `OPENAI_API_KEY` in your environment before running the simulator.
"""
import json
import os
import time

from openai import OpenAI

from utils import *

OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.environ.get("OPENAI_EMBED_MODEL",
                                    "text-embedding-3-small")

# The SDK picks up OPENAI_API_KEY from the environment automatically, but we
# pass it explicitly so that the failure mode when it's missing is a clear
# error at import time rather than a confusing 401 later.
_client = OpenAI(api_key=openai_api_key)


COMPLETION_SYSTEM_PROMPT = (
  "You are a text completion engine. You will be given a prompt that ends "
  "mid-sentence or mid-line. Your ONLY job is to complete that last line. "
  "Output ONLY the missing completion text — no explanations, no repetition "
  "of the prompt, no extra lines. Just the completion words."
)


def _openai_chat(prompt, temperature=0.7, max_tokens=1000, stop=None,
                 system_prompt=None):
  """Call OpenAI chat completions and return the text body."""
  messages = []
  if system_prompt:
    messages.append({"role": "system", "content": system_prompt})
  messages.append({"role": "user", "content": prompt})

  kwargs = {
    "model": OPENAI_CHAT_MODEL,
    "messages": messages,
    "temperature": temperature,
    "max_tokens": max_tokens,
  }
  if stop:
    kwargs["stop"] = stop

  try:
    resp = _client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""
  except Exception as e:
    print(f"  [WARN] OpenAI chat request failed: {e}", flush=True)
    return ""


def _strip_markdown_json(text):
  """Strip markdown code block wrappers like ```json ... ``` from LLM output."""
  text = text.strip()
  if text.startswith("```"):
    text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
      text = text[:-3]
  return text.strip()


def temp_sleep(seconds=0.1):
  time.sleep(seconds)


def ChatGPT_single_request(prompt):
  temp_sleep()
  return _openai_chat(prompt)


# ============================================================================
# #####################[SECTION 1: CHATGPT-3 STRUCTURE] ######################
# ============================================================================

def GPT4_request(prompt):
  """Given a prompt, call the chat model and return its response."""
  temp_sleep()
  try:
    return _openai_chat(prompt)
  except:
    print("ChatGPT ERROR")
    return "ChatGPT ERROR"


def ChatGPT_request(prompt):
  """Given a prompt, call the chat model and return its response."""
  try:
    return _openai_chat(prompt)
  except:
    print("ChatGPT ERROR")
    return "ChatGPT ERROR"


def GPT4_safe_generate_response(prompt,
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False):
  prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose:
    print("CHAT GPT PROMPT")
    print(prompt)

  for i in range(repeat):
    try:
      curr_gpt_response = _strip_markdown_json(GPT4_request(prompt))
      end_index = curr_gpt_response.rfind('}') + 1
      curr_gpt_response = curr_gpt_response[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]

      if func_validate(curr_gpt_response, prompt=prompt):
        return func_clean_up(curr_gpt_response, prompt=prompt)

      if verbose:
        print("---- repeat count: \n", i, curr_gpt_response)
        print(curr_gpt_response)
        print("~~~~")

    except:
      pass

  return False


def ChatGPT_safe_generate_response(prompt,
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False):
  prompt = '"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose:
    print("CHAT GPT PROMPT")
    print(prompt)

  for i in range(repeat):
    try:
      raw = _strip_markdown_json(ChatGPT_request(prompt))
      end_index = raw.rfind('}') + 1
      curr_gpt_response = raw[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]

      if func_validate(curr_gpt_response, prompt=prompt):
        return func_clean_up(curr_gpt_response, prompt=prompt)

      if verbose:
        print("---- repeat count: \n", i, curr_gpt_response)
        print(curr_gpt_response)
        print("~~~~")

    except Exception:
      pass

  return False


def ChatGPT_safe_generate_response_OLD(prompt,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False):
  if verbose:
    print("CHAT GPT PROMPT")
    print(prompt)

  for i in range(repeat):
    try:
      curr_gpt_response = ChatGPT_request(prompt).strip()
      if func_validate(curr_gpt_response, prompt=prompt):
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose:
        print(f"---- repeat count: {i}")
        print(curr_gpt_response)
        print("~~~~")

    except:
      pass
  print("FAIL SAFE TRIGGERED")
  return fail_safe_response


# ============================================================================
# ###################[SECTION 2: ORIGINAL GPT-3 STRUCTURE] ###################
# ============================================================================

def GPT_request(prompt, gpt_parameter):
  """Given a prompt and a dict of GPT parameters, call the chat model."""
  temp_sleep()
  try:
    return _openai_chat(
      prompt,
      temperature=gpt_parameter.get("temperature", 0.7),
      max_tokens=gpt_parameter.get("max_tokens", 1000),
      stop=gpt_parameter.get("stop", None),
      system_prompt=COMPLETION_SYSTEM_PROMPT,
    )
  except:
    print("TOKEN LIMIT EXCEEDED")
    return "TOKEN LIMIT EXCEEDED"


def generate_prompt(curr_input, prompt_lib_file):
  """
  Takes in the current input (e.g. comment that you want to classifiy) and
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this
  function replaces this substr with the actual curr_input to produce the
  final promopt that will be sent to the GPT3 server.
  ARGS:
    curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                INPUT, THIS CAN BE A LIST.)
    prompt_lib_file: the path to the promopt file.
  RETURNS:
    a str prompt that will be sent to OpenAI's GPT server.
  """
  if type(curr_input) == type("string"):
    curr_input = [curr_input]
  curr_input = [str(i) for i in curr_input]

  f = open(prompt_lib_file, "r")
  prompt = f.read()
  f.close()
  for count, i in enumerate(curr_input):
    prompt = prompt.replace(f"!<INPUT {count}>!", i)
  if "<commentblockmarker>###</commentblockmarker>" in prompt:
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
  return prompt.strip()


def safe_generate_response(prompt,
                           gpt_parameter,
                           repeat=5,
                           fail_safe_response="error",
                           func_validate=None,
                           func_clean_up=None,
                           verbose=False):
  if verbose:
    print(prompt)

  for i in range(repeat):
    curr_gpt_response = GPT_request(prompt, gpt_parameter)
    if func_validate(curr_gpt_response, prompt=prompt):
      return func_clean_up(curr_gpt_response, prompt=prompt)
    if verbose:
      print("---- repeat count: ", i, curr_gpt_response)
      print(curr_gpt_response)
      print("~~~~")
  return fail_safe_response


def get_embedding(text, model=None):
  """Return a single embedding vector for `text`."""
  if model is None:
    model = OPENAI_EMBED_MODEL
  text = text.replace("\n", " ")
  if not text:
    text = "this is blank"
  response = _client.embeddings.create(input=[text], model=model)
  return response.data[0].embedding


if __name__ == '__main__':
  gpt_parameter = {"engine": "text-davinci-003", "max_tokens": 50,
                   "temperature": 0, "top_p": 1, "stream": False,
                   "frequency_penalty": 0, "presence_penalty": 0,
                   "stop": ['"']}
  curr_input = ["driving to a friend's house"]
  prompt_lib_file = "prompt_template/test_prompt_July5.txt"
  prompt = generate_prompt(curr_input, prompt_lib_file)

  def __func_validate(gpt_response):
    if len(gpt_response.strip()) <= 1:
      return False
    if len(gpt_response.strip().split(" ")) > 1:
      return False
    return True
  def __func_clean_up(gpt_response):
    cleaned_response = gpt_response.strip()
    return cleaned_response

  output = safe_generate_response(prompt,
                                 gpt_parameter,
                                 5,
                                 "rest",
                                 __func_validate,
                                 __func_clean_up,
                                 True)

  print(output)
