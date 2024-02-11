from dotenv import load_dotenv
load_dotenv()
import os
import json
import time
from openai import OpenAI

import argparse
import numpy as np
from tqdm import tqdm


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--api_key_path', default='OPENAI_API_KEY.json', type=str, help='path for openai api key')
    args.add_argument('--prompt_path', default='', type=str, help='path for prompt')
    args.add_argument('--test_data_path', required=True, type=str, help='eval data path')
    args.add_argument('--inference_result_path', default='./', type=str, help='path for inference')
    args.add_argument('--output_file', default='prediction.json', type=str, help='outnput file name')
    return args.parse_args()

def run_engine(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125",
    messages=[{"role": "user", "content": 'Return a sql query:' + prompt}],
    temperature=0,
    max_tokens=512,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"])
    print()
    text = response.choices[0].message.content
    text = f'{text}'
    print(text)
    return text

if __name__ == '__main__':
    args = parse_args()

    with open(args.api_key_path) as f:
        OPENAI_API_KEY = json.load(f)

    if args.prompt_path == '':
        prompt = ''
    else:
        with open(args.prompt_path) as f:
            prompt = f.read()

    with open(args.test_data_path) as json_file:
        data = json.load(json_file)

    result = {}
    for line in tqdm(data):
        id_ = line['id']
        question = line['question']
        prompt_to_run = prompt
        while True:
            try:
                prompt_to_run = prompt_to_run.replace('TEST_QUESTION', question)
                pred = run_engine(prompt_to_run)
                break
            except KeyboardInterrupt:
                exit()
            except:
                time.sleep(60)
        result[id_] = pred

    os.makedirs(args.inference_result_path, exist_ok=True)
    out_file = os.path.join(args.inference_result_path, args.output_file)
    with open(out_file, 'w') as f:
        json.dump(result, f)