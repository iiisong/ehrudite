from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def process_data():
    data = request.get_json()
    text = data['text']
    processed_text = text.upper()
    return jsonify({'processed_text': processed_text})

if __name__ == '__main__':
    app.run(debug=True)