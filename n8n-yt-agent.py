import streamlit as st
import requests
import uuid
from PIL import Image  


# --- CONSTANTES ---
# URL de producción del webhook en n8n
WEBHOOK_URL = "https://liderdeequipo.app.n8n.cloud/webhook/invoke_agent"
# Token de autenticación para la cabecera 'API'
BEARER_TOKEN = "e5362baf-c777-4d57-a609-6eaf1f9e87f6"

def generate_session_id():
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    # 2. Envía el token directamente, sin el prefijo "Bearer "
    headers = {
        "API": BEARER_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    
    # Se añade un try-except para manejar mejor los errores de conexión o JSON
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()  # Esto generará un error para respuestas 4xx o 5xx
        
        # Verifica si la respuesta tiene contenido antes de intentar decodificar JSON
        if response.text:
            return response.json().get("output", "Error: La respuesta no contiene la clave 'output'.")
        else:
            return "Error: La respuesta del webhook está vacía."

    except requests.exceptions.HTTPError as http_err:
        return f"Error HTTP: {http_err} - {response.text}"
    except requests.exceptions.RequestException as req_err:
        return f"Error de Conexión: {req_err}"
    except ValueError: # Atrapa errores de decodificación JSON
        return f"Error: No se pudo decodificar la respuesta JSON. Respuesta recibida: {response.text}"

# --- EL RESTO DE TU CÓDIGO (main) PERMANECE IGUAL ---

def main():
    # --- MODIFICACIÓN PARA FAVICON LOCAL ---
    try:
        favicon = Image.open("assets/LogoTra.png")
    except FileNotFoundError:
        # Si no se encuentra el archivo, usa un emoji por defecto
        favicon = "🤖" 

    # 1. Configuración de la página con el favicon
    st.set_page_config(
        page_title="Dessau Softbot",
        page_icon=favicon, # Se pasa el objeto de la imagen
        layout="centered"
    )

    # 2. Título y subtítulo descriptivos basados en el manual
    st.title("Dessau Softbot")
    st.subheader("Asistente para la generación de informes demográficos del Perú")

    # --- RUTA DEL AVATAR ---
    bot_avatar_path = "assets/LogoTra.png"

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "¡Hola! Soy tu asistente inteligente para Dessau S&Z. Puedo generar informes en PDF o Word con datos demográficos, económicos y sociales del Perú. ¿Qué informe te gustaría crear hoy?"
        }]
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    # Despliegue de los mensajes del historial del chat
    for message in st.session_state.messages:
        # Se usa el avatar si el rol es 'assistant'
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar=bot_avatar_path):
                st.write(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    prompt = "¿En qué puedo ayudar?..."
    user_input = st.chat_input(prompt)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Pensando en mi respuesta..."):
            llm_response = send_message_to_llm(st.session_state.session_id, user_input)

        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        # Se muestra el nuevo mensaje del asistente también con su avatar
        with st.chat_message("assistant", avatar=bot_avatar_path):
            st.write(llm_response)

if __name__ == "__main__":
    main()

# cd "C:\Users\Merak Express\Documents\DessauArchivos\DessauAPP\n8n-streamlit-agent"
#streamlit run n8n-yt-agent.py
