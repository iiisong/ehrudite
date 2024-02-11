import os
import json
import pandas as pd

import torch
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

import mysql.connector
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text as sqltext
load_dotenv(find_dotenv())

from svs import SVS
from queryOpenAI import run_engine

# preloading slow things
model = SentenceTransformer('distilbert-multilingual-nli-stsb-quora-ranking')
f = open('../models/mimic-iii/qqdict.json')
qqdict = json.load(f)
corpus_embedding = torch.tensor(pd.read_csv("../models/mimic-iii/corpus.csv").values).to(torch.float32)

client = OpenAI(api_key=os.getenv("OAI_KEY"))

conn_string = f'mysql+mysqlconnector://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}'
engine = create_engine(conn_string, echo=True)
conn = engine.connect()

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def handle_all():
    data = request.get_json()
    text = data['text']

    qqlist = [qqdict[str(i)] for i in SVS(text, k=30, corpus=corpus_embedding, model=model)]

    relevant_qtext = "# Q: \t" + "\n# Q: \t".join(["\n# A: \t".join(rel) for rel in qqlist])
    test_prompt = open('../models/mimic-iii/codex_apidoc.txt').read()

    max_iter = 3

    result = None
    for i in range(max_iter):
        print(test_prompt)
        print()
        try:
            pred_query = run_engine(question, test_prompt, relevant_qtext)
            result = conn.execute(sqltext(pred_query)).fetchall()

            if len(result) == 0:
                test_prompt = "0 rows returned, try again.\n" + test_prompt
                continue

            break
        except Exception as e:
            test_prompt = str(e) + "\n" + test_prompt
            print(e)
    sim_questions = qqlist
    query = pred_query
    results = results

    try:
        response = requests.post('http://localhost:4000/create-message', json={'prompt': text, 'query':query, 'response_text': results})
        response.raise_for_status()
    except requests.RequestException as e:
        print('Error making POST request:', e)

    return jsonify({'sim_questions': sim_questions, 'query': query, 'results': results})