import os
# بالای فایل، بعد از importها این خط رو اضافه کن
from flask import Flask, request, jsonify, Response, session, send_from_directory, url_for
from utils import check_rate_limit, perform_stt, build_llm_messages, stream_llm_generator
from config import generate
import uuid
import threading

app = Flask(__name__,)
app.secret_key = 'my_secret_key' 


@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    user_id = session['user_id']
    session_id = request.args.get('session_id') 

    if session_id and session_id not in conversation_history:
        conversation_history[session_id] = []
    else:
        conversation_history[session_id] = []

    return send_from_directory('static/html', 'index.html')





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4001)  