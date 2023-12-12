import openai
from openai import OpenAI


from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import uuid
import os

from utils import convert_docx_to_txt

openai.api_key = os.environ.get("OPENAI_API_KEY") 

CLIENT = OpenAI()
SYSTEM_PROMPT = """
You are an AI assistant that answers peoples questions!
"""

FILE_UPLOAD_PROMPT = """
Here is a txt file named {filename} that you should reference for the remainder of the conversation.
```
{file}
```
"""

app = Flask(__name__)
CORS(app)

# all conversations will be stored in this dict
# sessionid: [messages]
conversations = {}

# get the model response from the OpenAI API
def get_response(messages):
    response = CLIENT.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    return response

@app.route('/get-messages', methods=['POST'])
def get_messages():

    data = request.get_json()

    # get the session id from the request
    session_id = data['session_id']

    if not session_id in conversations:
        return Response(status=400)

    # return the conversation
    return jsonify({"messages": conversations[session_id][1:]}), 200

@app.route('/session', methods=['POST'])
def session():
    
    data = request.get_json()

    if 'session_id' not in data:
        session_id = str(uuid.uuid4())
        conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    else:
        # get the session id from the request
        session_id = data['session_id']

    if session_id not in conversations:
        session_id = str(uuid.uuid4())
        conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # return the session id
    return jsonify({"session_id": session_id}), 200

@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return {}, 400

    file = request.files['file']

    if file.filename == '':
        return {}, 400
    
    # get the session id from the request
    session_id = request.form['session_id']

    if not session_id in conversations:
        return {}, 400
    
    # ensure filename ends with .txt
    if not (file.filename.endswith('.txt') or file.filename.endswith('.docx')):
        return {}, 400

    # if the file is a docx, convert it to a txt file
    if file.filename.endswith('.docx'):
        text = convert_docx_to_txt(file)
    else:
        # read the file
        text = file.read().decode('utf-8')

    # add the file to the conversation
    conversations[session_id][0]["content"] += FILE_UPLOAD_PROMPT.format(filename=file.filename, file=text)

    # return the response
    return {}, 200
    


@app.route('/chat', methods=['POST'])
def chat():

    data = request.get_json()

    if 'session_id' not in data or 'message' not in data:
        return '', 400

    # get the session id from the request
    session_id = data['session_id']
    # get the message from the request
    message = data['message']

    if not message:
        return Response(status=400)

    if not session_id in conversations:
        return Response(status=400)

    # add the message to the conversation
    conversations[session_id].append({"role": "user", "content": message})

    # get the response from the OpenAI API
    response = get_response(conversations[session_id])

    # get the message from the chat completion object
    message = response.choices[0].message.content

    # add the response to the conversation
    conversations[session_id].append({"role": "assistant", "content": response.choices[0].message.content})

    # return the response
    return jsonify({"role":"assistant","content":message}), 200


def main():
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()

    








