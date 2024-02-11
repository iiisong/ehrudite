import os
import json
import pandas as pd

import torch
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

from flask import Flask, request, jsonify, make_response
import requests

import mysql.connector
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text as sqltext
load_dotenv(find_dotenv())

import sys
sys.path.append('../../')

from interface.backend.svs import SVS
from interface.backend.queryOpenAI import run_engine

print("Current working directory:", os.getcwd())

model = SentenceTransformer('distilbert-multilingual-nli-stsb-quora-ranking')
f = open('../../models/mimic-iii/qqdict.json')
qqdict = json.load(f)
corpus_embedding = torch.tensor(pd.read_csv("../../models/mimic-iii/corpus.csv").values).to(torch.float32)

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
    test_prompt = open('../../models/mimic-iii/codex_apidoc.txt').read()

    max_iter = 3

    results = ""
    for i in range(max_iter):
        print(test_prompt)
        print()
        try:
            pred_query = run_engine(text, test_prompt, relevant_qtext)
            results = conn.execute(sqltext(pred_query)).fetchall()

            if len(results) == 0:
                test_prompt = "0 rows returned, try again.\n" + test_prompt
                continue

            break
        except Exception as e:
            test_prompt = str(e) + "\n" + test_prompt
            print(e)
    sim_questions = qqlist
    query = pred_query

    # results = jsonify({'result': [dict(row) for row in results]})
    results = str(results)
    query = str(query)

    try:
        response = requests.post('http://localhost:4000/create-message', json={'prompt': text, 'query':query, 'response_text': results})
        response.raise_for_status()
    except requests.RequestException as e:
        print('Error making POST request:', e)

    return make_response(jsonify({'sim_questions': sim_questions, 'query': query, 'results': results}),200)

@app.route('/data-query', methods=['POST'])
def handle_query():
    data = request.get_json()
    query = data['text']

    max_iter = 3

    results = conn.execute(sqltext(query)).fetchall()

    # results = jsonify({'result': [dict(row) for row in results]})
    results = str(results)
    query = str(query)

    return make_response(jsonify({'query': query, 'results': results}),200)

if __name__ == '__main__':
    app.run(debug=True)