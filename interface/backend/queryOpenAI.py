import os
from openai import OpenAI

import argparse
import numpy as np

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OAI_KEY"))

test_prompt = open('../../models/mimic-iii/codex_apidoc.txt').read()

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--question', type=str, help='text question for SQL query')
    args.add_argument('--prompt_path', default='../../models/mimic-iii/codex_apidoc.txt', type=str, help='path for prompt')
    return args.parse_args()

def run_engine(prompt, prompt_template=test_prompt, svs=""):
    decorated_prompt = svs + prompt_template.replace('TEST_QUESTION', prompt)

    print(decorated_prompt)

    client = OpenAI(api_key=os.getenv("OAI_KEY"))
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": 'Return a sql query:' + decorated_prompt}],
        temperature=0,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["#", ";"])

    print()
    query = response.choices[0].message.content
    query = f'select{query};'.upper()
    return query

if __name__ == '__main__':
    args = parse_args()

    if args.prompt_path == '':
        prompt_template = "TEST_QUESTION"
    else:
        with open(args.prompt_path) as f:
            prompt_template = f.read()

    question = args.question
    query = run_engine(question, prompt_template=prompt_template)

    print(query)
