const login = document.querySelector(".login");
const loginForm = login.querySelector(".login__form");
const loginInput = login.querySelector(".login__input");
const backButton = document.querySelector(".back-button");
const formSelector = document.getElementById("seletor_idiomas");

const chat = document.querySelector(".chat");
const chatForm = chat.querySelector(".chat__form");
const chatInput = chat.querySelector(".chat__input");
const chatMessages = chat.querySelector(".chat__messages");

const colors = ["cadetblue", "darkgoldenrod", "cornflowerblue", "darkkhaki", "hotpink", "gold"];
const user = { id: "", name: "", color: "", lang: "" };
let socket;

// Cria mensagens
const createMessageSelfElement = content => {
  const div = document.createElement("div");
  div.classList.add("message--self");
  div.textContent = content;
  return div;
};

const createMessageOtherElement = (content, sender, senderColor) => {
  const div = document.createElement("div");
  div.classList.add("message--other");
  const span = document.createElement("span");
  span.classList.add("message--sender");
  span.style.color = senderColor;
  span.textContent = sender + ": ";
  div.appendChild(span);
  div.append(content);
  return div;
};

const scrollScreen = () => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });

// Alterna telas
function showScreen(screen) {
  login.style.display = "none";
  chat.style.display = "none";
  formSelector.style.display = "none";

  if (screen === "login") login.style.display = "flex";
  if (screen === "idioma") formSelector.style.display = "flex";
  if (screen === "chat") chat.style.display = "flex";
}

// Inicia na tela de idioma
showScreen("idioma");
history.replaceState({ screen: "idioma" }, "");

// LOGIN
const handleLogin = event => {
  event.preventDefault();
  user.id = crypto.randomUUID();
  user.name = loginInput.value;
  user.color = colors[Math.floor(Math.random() * colors.length)];
  user.lang = document.getElementById("idiomas_select").value;

  if (!user.name || !user.lang) {
    alert("Por favor, preencha o nome e selecione o idioma.");
    return;
  }

  showScreen("chat");
  history.pushState({ screen: "chat" }, "");

  //socket = io();  // se conecta automaticamente ao mesmo host
  socket = io("wss://realtime-chat-backend.onrender.com", {
  transports: ["websocket"],
});


  socket.on("connect", () => {
    socket.emit("register_user", {
      id: user.id,
      name: user.name,
      color: user.color,
      lang: user.lang
    });
  });

  socket.on("chat_message", data => {
    const message = data.userId === user.id
      ? createMessageSelfElement(data.content)
      : createMessageOtherElement(data.content, data.userName, data.userColor);

    chatMessages.appendChild(message);
    scrollScreen();
  });
};

// Envia mensagem
const sendMessage = event => {
  event.preventDefault();
  if (!chatInput.value.trim()) return;

  const message = {
    userId: user.id,
    userName: user.name,
    userColor: user.color,
    content: chatInput.value
  };

  socket.emit("message", message);
  chatInput.value = "";
};

// Eventos
loginForm.addEventListener("submit", handleLogin);
chatForm.addEventListener("submit", sendMessage);

// Voltar botão
backButton.addEventListener("click", () => {
  showScreen("idioma");
  history.pushState({ screen: "idioma" }, "");
});

// Troca idioma de interface
const select = document.getElementById("idiomas_select");
const textos = {
  pt: { loginTitulo: "Login", loginBotao: "Entrar", voltar: "Voltar", loginPlaceholder: "Seu nome", chatPlaceholder: "Digite uma mensagem" },
  en: { loginTitulo: "Login", loginBotao: "Enter", voltar: "Back", loginPlaceholder: "Your name", chatPlaceholder: "Type a message" },
  es: { loginTitulo: "Inicio de sesión", loginBotao: "Entrar", voltar: "Volver", loginPlaceholder: "Tu nombre", chatPlaceholder: "Escribe un mensaje" }
};

select.addEventListener("change", () => {
  const idioma = select.value;
  if (textos[idioma]) {
    login.querySelector("h2").textContent = textos[idioma].loginTitulo;
    login.querySelector(".login__button").textContent = textos[idioma].loginBotao;
    login.querySelector(".login__input").placeholder = textos[idioma].loginPlaceholder;
    backButton.textContent = textos[idioma].voltar;
    chatInput.placeholder = textos[idioma].chatPlaceholder;
  }
  showScreen("login");
  history.pushState({ screen: "login" }, "");
});
