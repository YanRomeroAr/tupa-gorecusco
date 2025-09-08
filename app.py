import streamlit as st
import openai
import time
import re
from typing import Optional

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
st.set_page_config(
    page_title="Asistente TUPA",
    page_icon="🏛️",
    layout="centered"
)

try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError:
    st.error("⚠️ Configuración requerida")
    st.stop()

# ---------------------------
# ESTILOS CHATGPT-LIKE
# ---------------------------
st.markdown("""
<style>
    .stApp {
        background: #343541;
        color: #ffffff;
    }
    
    /* Header compacto */
    .header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #444654;
        margin-bottom: 1rem;
    }
    
    .header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .header p {
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
        color: #8e8ea0;
    }

    /* Chat messages estilo ChatGPT */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0 !important;
        border: none !important;
        margin: 0 !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: #343541 !important;
    }
    
    .stChatMessage[data-testid="user-message"] > div {
        background: #343541 !important;
        color: #ffffff !important;
        padding: 1rem !important;
        border-radius: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        border-bottom: 1px solid #444654 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: #444654 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] > div {
        background: #444654 !important;
        color: #ffffff !important;
        padding: 1rem !important;
        border-radius: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        border-bottom: 1px solid #343541 !important;
    }

    /* Input estilo ChatGPT */
    .stChatInputContainer {
        background: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }
    
    .stChatInputContainer input {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stChatInputContainer input::placeholder {
        color: #8e8ea0 !important;
    }
    
    .stChatInputContainer button {
        background: #10a37f !important;
        border: none !important;
        color: white !important;
        padding: 0.5rem !important;
        margin: 0.25rem !important;
        border-radius: 4px !important;
    }

    /* Sugerencias compactas */
    .suggestions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
        margin: 1rem 0;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .suggestion {
        background: #444654;
        border: 1px solid #565869;
        border-radius: 8px;
        padding: 0.75rem;
        color: #ffffff;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        text-align: left;
    }
    
    .suggestion:hover {
        background: #565869;
        border-color: #676b7d;
    }
    
    .suggestion-icon {
        margin-right: 0.5rem;
    }

    /* Loading */
    .loading {
        background: #444654;
        color: #ffffff;
        padding: 1rem;
        border-bottom: 1px solid #343541;
    }
    
    .dots {
        display: inline-flex;
        gap: 4px;
        margin-left: 0.5rem;
    }
    
    .dot {
        width: 4px;
        height: 4px;
        background: #ffffff;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes typing {
        0%, 80%, 100% { opacity: 0.3; }
        40% { opacity: 1; }
    }

    /* Ocultar sidebar por defecto */
    .css-1d391kg { display: none; }
    
    /* Responsive */
    @media (max-width: 768px) {
        .suggestions {
            grid-template-columns: 1fr;
        }
    }
    
    /* Ocultar elementos streamlit */
    footer { display: none; }
    header[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# FUNCIONES
# ---------------------------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

def create_thread():
    try:
        thread = openai.beta.threads.create()
        return thread.id
    except:
        return None

def send_message(thread_id: str, content: str):
    try:
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user", 
            content=content
        )
        return True
    except:
        return False

def get_response(thread_id: str):
    try:
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        for _ in range(30):
            status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                return None
            time.sleep(1)
        
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        for msg in messages.data:
            if msg.role == "assistant":
                return re.sub(r'【\d+:.*?】', '', msg.content[0].text.value).strip()
        return None
    except:
        return None

def process_query(query: str):
    if not st.session_state.thread_id:
        st.session_state.thread_id = create_thread()
    
    st.session_state.messages.append(("user", query))
    
    # Loading
    with st.empty():
        st.markdown('<div class="loading">Procesando<div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>', unsafe_allow_html=True)
        
        if send_message(st.session_state.thread_id, query):
            response = get_response(st.session_state.thread_id)
            if response:
                st.session_state.messages.append(("assistant", response))
            else:
                st.session_state.messages.append(("assistant", "Error procesando consulta"))

# ---------------------------
# INTERFAZ PRINCIPAL
# ---------------------------
init_session()

# Header compacto
st.markdown("""
<div class="header">
    <h1>🏛️ Asistente TUPA</h1>
    <p>Gobierno Regional del Cusco</p>
</div>
""", unsafe_allow_html=True)

# Sugerencias solo si no hay mensajes
if not st.session_state.messages:
    
    # Botones funcionales
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Licencia de Funcionamiento", use_container_width=True):
            process_query("¿Qué documentos necesito para una licencia de funcionamiento?")
            st.rerun()
            
        if st.button("⏰ Horarios de Atención", use_container_width=True):
            process_query("¿Cuáles son los horarios de atención?")
            st.rerun()
    
    with col2:
        if st.button("🏗️ Permisos de Construcción", use_container_width=True):
            process_query("¿Cuánto demora un permiso de construcción?")
            st.rerun()
            
        if st.button("💰 Tasas y Costos", use_container_width=True):
            process_query("¿Cuánto cuesta un certificado de zonificación?")
            st.rerun()

# Mostrar chat
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.write(message)

# Input
if prompt := st.chat_input("Mensaje Asistente TUPA..."):
    process_query(prompt)
    st.rerun()

# Botón limpiar en sidebar
with st.sidebar:
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.session_state.thread_id = None
        st.rerun()
