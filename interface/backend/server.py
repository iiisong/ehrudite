from flask import Flask, request, jsonify
import sys
sys.path.append('../..')
from EHRSQL.gpt import codex

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def process_data():
    data = request.get_json()
    text = data['text']
    processed_text = process_text(text)
    return jsonify({'processed_text': processed_text})

def process_text(text):
    response_text = codex.run_engine(text)
    #is result valid query
        #loop below if returned rerun or 5 trials
            #call next function
    #else
        #return jsonify({'processed_text': need more info})
    #RETURN FINAL RESULT BELOW
    return response_text

# def next():
    # query database
    #success?
        #return 
    #else
        #return 'rerun'

if __name__ == '__main__':
    app.run(debug=True)