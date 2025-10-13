import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from googletrans import Translator

# Diretórios do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))

# Criação da aplicação Flask
def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        template_folder=os.path.join(BASE_DIR, "templates")
    )
    app.config['SECRET_KEY'] = os.urandom(24)  # chave secreta segura
    return app

app = create_app()

# Configuração do Flask-SocketIO com Eventlet
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Dicionário de usuários conectados
users = {}

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Novo cliente conectado: {request.sid}")

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
        'name': data.get('name'),
        'color': data.get('color'),
        'lang': data.get('lang'),
        'sid': request.sid
    }
    print("Usuário registrado:", users[user_id])

@socketio.on('message')
def handle_message(data):
    # Garantir que o Translator rode dentro do contexto do evento
    translator = Translator()

    sender_id = data.get('userId')
    sender_name = data.get('userName')
    sender_color = data.get('userColor')
    original_text = data.get('content', '')

    print(f"Mensagem recebida de {sender_name}: {original_text}")

    # Envia a mensagem traduzida para cada usuário
    for uid, info in users.items():
        try:
            target_lang = info.get('lang', 'en')  # fallback para inglês
            translated_text = translator.translate(original_text, dest=target_lang).text

            socketio.emit('chat_message', {
                'userId': sender_id,
                'userName': sender_name,
                'userColor': sender_color,
                'content': translated_text
            }, room=info['sid'])
        except Exception as e:
            print(f"Erro na tradução para {uid}: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Debug False para produção; host 0.0.0.0 necessário no Render
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
