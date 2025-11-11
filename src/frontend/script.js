const API_URL = "/mensagem/";

async function enviarMensagem() {
  const input = document.getElementById("input");
  const messages = document.getElementById("messages");
  const texto = input.value.trim();
  if (!texto) return;

  // Exibe mensagem do usuário
  messages.innerHTML += `<div class="message user">${texto}</div>`;
  input.value = "";

  try {
    const res = await fetch(`${API_URL}?texto=${encodeURIComponent(texto)}`);
    const data = await res.json();

    // Exibe resposta do bot
    messages.innerHTML += `
      <div class="message bot">
        ${data.mensagem}
      </div>`;
  } catch (err) {
    messages.innerHTML += `<div class="message bot">❌ Erro ao conectar com o servidor.</div>`;
  }

  messages.scrollTop = messages.scrollHeight;
}

// Envia com Enter
document.getElementById("input").addEventListener("keypress", e => {
  if (e.key === "Enter") enviarMensagem();
});
