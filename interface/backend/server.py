from flask import Flask, request, jsonify
import sys
import requests
sys.path.append('../../')
from genai import queryOpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import mysql.connector

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def process_data():
    data = request.get_json()
    text = data['text']
    processed_text = process_text(text)
    return jsonify({'processed_text': processed_text})

def process_text(text):
    response_text = queryOpenAI.run_engine(text)
    response_text = query(response_text)
    counter = 0
    while(response_text == "Invalid query" and counter < 3):
        response_text = queryOpenAI.run_engine("That query was invalid, " + text)
        response_text = query(response_text)
        counter += 1
    try:
        response = requests.post('http://localhost:4000/create-message', json={'prompt': text, 'response_text': response_text})
        response.raise_for_status()
    except requests.RequestException as e:
        print('Error making POST request:', e)
    return response_text

def query(script):
    connection = mysql.connector.connect(
        host= os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        passwd= os.getenv("DB_PASSWORD"),
        db= os.getenv("DB_NAME")
    )
    cursor = connection.cursor()
    try:
        cursor.execute(script.upper())
        return cursor.fetchone()
    except:
        return "Invalid query"

if __name__ == '__main__':
    app.run(debug=True)