import os
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from googletrans import Translator
from flask_cors import CORS
from threading import Lock

# Diretórios do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))

def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        template_folder=os.path.join(BASE_DIR, "templates")
    )
    app.config['SECRET_KEY'] = os.urandom(24)
    CORS(app)
    return app

app = create_app()
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

users = {}
users_lock = Lock()
translator = Translator()  # Reutiliza instância
translation_cache = {}     # Cache para acelerar mensagens repetidas

@app.route('/')
def home():
    return "Servidor WebSocket do Chat Realtime está ativo 🚀"

@socketio.on('connect')
def handle_connect():
    print(f"Novo cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    with users_lock:
        disconnected = [uid for uid, info in users.items() if info['sid'] == request.sid]
        for uid in disconnected:
            print(f"Usuário desconectado: {users[uid]['name']}")
            del users[uid]

@socketio.on('register_user')
def register_user(data):
    with users_lock:
        user_id = data['id']
        users[user_id] = {
            'name': data.get('name'),
            'color': data.get('color'),
            'lang': data.get('lang'),
            'sid': request.sid
        }
        print("Usuário registrado:", users[user_id])

@socketio.on('message')
def handle_message(data):
    sender_id = data.get('userId')
    sender_name = data.get('userName')
    sender_color = data.get('userColor')
    original_text = data.get('content', '')

    print(f"Mensagem recebida de {sender_name}: {original_text}")

    with users_lock:
        current_users = list(users.items())

    for uid, info in current_users:
        target_lang = info.get('lang', 'en')
        cache_key = (original_text, target_lang)
        translated_text = translation_cache.get(cache_key)

        if not translated_text:
            try:
                start_time = time.time()
                translated = translator.translate(original_text, dest=target_lang)
                translated_text = translated.text
                translation_cache[cache_key] = translated_text
                elapsed = time.time() - start_time
                print(f"Tradução concluída em {elapsed:.2f}s → {target_lang}")
            except Exception as e:
                print(f"[⚠️ Erro de tradução → {target_lang}] {e}")
                translated_text = original_text  # fallback imediato

        socketio.emit('chat_message', {
            'userId': sender_id,
            'userName': sender_name,
            'userColor': sender_color,
            'content': translated_text
        }, room=info['sid'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
