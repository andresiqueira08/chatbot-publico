from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid

# Funções 
from dialogflow_api import detectar_intencao
from bd import buscar_resposta


import os, json
from google.oauth2 import service_account

# Lê a variável de ambiente
credenciais_json = os.getenv("GOOGLE_CREDENTIALS")

if credenciais_json:
    credenciais = service_account.Credentials.from_service_account_info(json.loads(credenciais_json))
else:
    credenciais = service_account.Credentials.from_service_account_file("chave-maria.json")

app = FastAPI()
PROJECT_ID = "maria-wfbd"

# 🔓 Permite que o frontend se comunique com o backend (importante para deploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, use o domínio do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho absoluto do frontend
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")

@app.get("/")
def serve_frontend():
    """Serve o arquivo HTML principal na raiz"""
    return FileResponse(frontend_path)

@app.get("/mensagem/")
def responder(texto: str, usuario: str | None = None):
    """Endpoint para processar a mensagem do usuário"""
    if not usuario:
        usuario = str(uuid.uuid4())[:8]

    # 1️⃣ Tenta buscar no banco local
    for palavra in texto.split():
        resposta_bd = buscar_resposta(palavra)
        if resposta_bd:
            return {"origem": "banco_de_dados", "mensagem": resposta_bd, "palavra": palavra}

    # 2️⃣ Tenta buscar no Dialogflow
    resultado = detectar_intencao(PROJECT_ID, usuario, texto, "pt-BR")

    if resultado and resultado.fulfillment_text:
        return {
            "origem": "dialogflow",
            "mensagem": resultado.fulfillment_text,
            "intencao": resultado.intent.display_name
        }

    # 3️⃣ Caso nenhum reconheça
    return {
        "origem": "nenhuma",
        "mensagem": "Não encontrei resposta no banco nem no Dialogflow.",
        "intencao": "Default Fallback Intent"
    }
