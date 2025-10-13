from flask import Flask, render_template, request
from flask_socketio import SocketIO
from googletrans import Translator
import os

# Caminho absoluto da pasta atual (onde este app.py está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para a pasta frontend (2 níveis acima)
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../frontend"))

# Cria o app Flask apontando para o frontend como static e templates na pasta python/templates
app = Flask(__name__,
            static_folder=STATIC_DIR,
            template_folder=os.path.join(BASE_DIR, "templates"))

socketio = SocketIO(app, cors_allowed_origins="*")
translator = Translator()

users = {}

@app.route('/')
def home():
    # renderiza o index.html que está em backend/python/templates/
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print("Novo cliente conectado!")


@socketio.on('disconnect')
def handle_disconnect():
    disconnected = [uid for uid, info in users.items() if info['sid'] == request.sid]
    for uid in disconnected:
        print(f"Usuário desconectado: {users[uid]['name']}")
        del users[uid]


@socketio.on('register_user')
def register_user(data):
    user_id = data['id']
    users[user_id] = {
        'name': data['name'],
        'color': data['color'],
        'lang': data['lang'],
        'sid': request.sid
    }
    print(f"Usuário registrado: {users[user_id]}")


@socketio.on('message')
def handle_message(data):
    sender_id = data['userId']
    sender_name = data['userName']
    sender_color = data['userColor']
    original_text = data['content']

    print(f"Mensagem recebida de {sender_name}: {original_text}")

    for uid, info in users.items():
        try:
            target_lang = info['lang']
            translated_text = translator.translate(original_text, dest=target_lang).text

            socketio.emit('chat_message', {
                'userId': sender_id,
                'userName': sender_name,
                'userColor': sender_color,
                'content': translated_text
            }, room=info['sid'])
        except Exception as e:
            print("Erro na tradução:", e)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
