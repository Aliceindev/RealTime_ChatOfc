import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from googletrans import Translator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Caminho absoluto para a pasta frontend (a partir da raiz do repo)
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,                     # arquivos estáticos (css/js/images)
    template_folder=os.path.join(BASE_DIR, "templates")  # templates (index.html)
)

# Permitir CORS para todos, usar eventlet no deploy para websocket
socketio = SocketIO(app, cors_allowed_origins="*")

translator = Translator()
users = {}

@app.route('/')
def home():
    # Se index.html estiver na pasta backend/python/templates, renderiza.
    # Se você preferir servir o index diretamente do frontend/static, pode usar:
    # return app.send_static_file('index.html')
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Novo cliente conectado!", request.sid)

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
    sender_id = data.get('userId')
    sender_name = data.get('userName')
    sender_color = data.get('userColor')
    original_text = data.get('content', '')
    print(f"Mensagem recebida de {sender_name}: {original_text}")

    for uid, info in users.items():
        try:
            target_lang = info.get('lang')
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
    # Porta que o Render fornece estará em PORT; senão usar 5000 localmente.
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
