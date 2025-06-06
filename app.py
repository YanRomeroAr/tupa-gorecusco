import streamlit as st
import openai
import time
import re
from typing import List, Tuple, Optional

# ---------------------------
# CONFIGURACIÓN DE PÁGINA (DEBE SER LO PRIMERO)
# ---------------------------
st.set_page_config(
    page_title="Asistente TUPA - Gore Cusco", 
    page_icon="🤖", 
    layout="centered"
)

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
@st.cache_data
def load_config():
    """Carga la configuración de la aplicación"""
    return {
        "page_title": "Asistente TUPA - Gore Cusco",
        "page_icon": "🤖",
        "logo_url": "https://goresedetramitedigital.regioncusco.gob.pe/filest/images/logoRegion.png",
        "title": "Demo - Bot del TUPA Gore Cusco",
        "description": "Haz tus consultas sobre el Texto Único de Procedimientos Administrativos (TUPA) del Gobierno Regional del Cusco y obtén respuestas claras, rápidas y confiables sobre requisitos, plazos y costos de cada trámite."
    }

config = load_config()

# Configuración de OpenAI
try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# ---------------------------
# ESTILOS PERSONALIZADOS
# ---------------------------
def apply_custom_styles():
    """Aplica estilos CSS personalizados"""
    st.markdown("""
        <style>
            /* Estilos generales */
            html, body, .stApp {
                background-color: white !important;
                color: black !important;
            }
            
            /* Estilos de texto */
            .stMarkdown h1, .stMarkdown h2, .stMarkdown p,
            .stChatMessage p, .stChatMessage ul, .stChatMessage ol, 
            .stChatMessage li, .stChatMessage span, .stChatMessage div {
                color: black !important;
            }
            
            /* Header con logo y título */
            .header-container {
                display: flex;
                align-items: center;
                gap: 20px;
                margin-bottom: 20px;
                padding: 10px 0;
            }
            
            .header-logo {
                flex-shrink: 0;
            }
            
            .header-text {
                flex-grow: 1;
            }
            
            .header-text h1 {
                margin: 0 !important;
                font-size: 2.5rem !important;
                font-weight: 600 !important;
            }
            
            /* Estilos del input */
            input[type="text"] {
                background-color: white !important;
                color: black !important;
                border: 2px solid #ddd !important;
                border-radius: 25px !important;
                padding: 12px 20px !important;
                transition: border-color 0.3s ease;
            }
            
            input[type="text"]:focus {
                border-color: #007bff !important;
                box-shadow: 0 0 0 3px rgba(0,123,255,0.25) !important;
            }
            
            input[type="text"]::placeholder {
                color: #888 !important;
            }
            
            /* Botón de envío */
            .stChatInputContainer button {
                background-color: #007bff !important;
                color: white !important;
                border: 2px solid #007bff !important;
                border-radius: 25px !important;
                transition: all 0.3s ease;
            }
            
            .stChatInputContainer button:hover {
                background-color: #0056b3 !important;
                border-color: #0056b3 !important;
            }
            
            /* Responsivo */
            @media (max-width: 768px) {
                .header-container {
                    flex-direction: column;
                    text-align: center;
                    gap: 15px;
                }
                
                .header-text h1 {
                    font-size: 2rem !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# ---------------------------
# HEADER CON LOGO Y TÍTULO
# ---------------------------
def render_header():
    """Renderiza el header con logo y título lado a lado"""
    st.markdown(f"""
        <div class="header-container">
            <div class="header-logo">
                <img src="{config['logo_url']}" width="120" alt="Logo Gore Cusco">
            </div>
            <div class="header-text">
                <h1>{config['title']}</h1>
                <p style="margin: 10px 0 0 0; font-size: 1.1rem; color: #666;">
                    {config['description']}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

render_header()

# ---------------------------
# GESTIÓN DE ESTADO
# ---------------------------
def init_session_state():
    """Inicializa el estado de la sesión"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "historial_preguntas" not in st.session_state:
        st.session_state.historial_preguntas = []

init_session_state()

# ---------------------------
# FUNCIONES AUXILIARES
# ---------------------------
def is_contextual_query(user_input: str) -> bool:
    """Determina si la consulta es contextual basada en palabras clave"""
    frases_contextuales = [
        "no entendí", "explica", "dudas", "más claro", "más simple", "no me parece",
        "repite", "aclara", "sencillo", "para qué sirve", "cuál es el objetivo", 
        "qué finalidad tiene", "por qué se hace", "qué implica", "cuál es el propósito",
        "a qué se refiere", "qué significa esto", "no quedó claro", "detalla mejor",
        "en otras palabras", "hazlo más fácil", "explícame mejor", "no me queda claro"
    ]
    return any(frase in user_input.lower() for frase in frases_contextuales)

def clean_response(response: str) -> str:
    """Limpia la respuesta removiendo referencias innecesarias"""
    return re.sub(r'【\d+:.*?†.*?】', '', response)

def create_new_thread() -> str:
    """Crea un nuevo hilo de conversación"""
    try:
        thread = openai.beta.threads.create()
        return thread.id
    except Exception as e:
        st.error(f"Error al crear hilo de conversación: {e}")
        return None

def send_message_to_assistant(thread_id: str, content: str) -> bool:
    """Envía un mensaje al asistente"""
    try:
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        return True
    except Exception as e:
        st.error(f"Error al enviar mensaje: {e}")
        return False

def run_assistant(thread_id: str) -> Optional[str]:
    """Ejecuta el asistente y obtiene la respuesta"""
    try:
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Esperar a que complete
        max_attempts = 60  # Máximo 60 segundos
        attempts = 0
        
        while attempts < max_attempts:
            status_info = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if status_info.status == "completed":
                break
            elif status_info.status == "failed":
                st.error("Error al procesar la respuesta del asistente")
                return None
            
            time.sleep(1)
            attempts += 1
        
        if attempts >= max_attempts:
            st.error("Tiempo de espera agotado")
            return None
        
        # Obtener mensajes
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        
        for msg in messages.data:
            if msg.role == "assistant":
                return clean_response(msg.content[0].text.value)
        
        return None
        
    except Exception as e:
        st.error(f"Error al ejecutar asistente: {e}")
        return None

def process_user_input(user_input: str):
    """Procesa la entrada del usuario y genera respuesta"""
    # Determinar si es consulta contextual
    es_contextual = is_contextual_query(user_input)
    
    # Preparar el prompt
    if es_contextual and st.session_state.historial_preguntas and st.session_state.thread_id:
        referencia = st.session_state.historial_preguntas[-1]
        prompt = f"Responde con más claridad sobre esto: {referencia}. Pregunta actual: {user_input}"
    else:
        prompt = user_input
        # Crear nuevo hilo si no existe o no es contextual
        if not st.session_state.thread_id or not es_contextual:
            st.session_state.thread_id = create_new_thread()
            if not st.session_state.thread_id:
                return
        
        # Agregar al historial
        st.session_state.historial_preguntas.append(user_input)
    
    # Agregar mensaje del usuario al chat
    st.session_state.messages.append(("usuario", user_input))
    
    # Enviar mensaje al asistente
    if not send_message_to_assistant(st.session_state.thread_id, prompt):
        return
    
    # Obtener respuesta
    with st.spinner("🤖 Generando respuesta..."):
        respuesta = run_assistant(st.session_state.thread_id)
        
        if respuesta:
            st.session_state.messages.append(("asistente", respuesta))
        else:
            st.session_state.messages.append(("asistente", "Lo siento, hubo un error al procesar tu consulta. Por favor, intenta nuevamente."))

# ---------------------------
# INTERFAZ PRINCIPAL
# ---------------------------
def render_chat_history():
    """Renderiza el historial del chat"""
    for rol, mensaje in st.session_state.messages:
        with st.chat_message("user" if rol == "usuario" else "assistant"):
            st.markdown(mensaje)

# Mostrar historial del chat
render_chat_history()

# Input del usuario - Solo una vez por ejecución
user_input = st.chat_input("💬 Escribe tu consulta sobre el TUPA aquí...")

if user_input:
    process_user_input(user_input)

# Input del usuario
user_input = st.chat_input("💬 Escribe tu consulta sobre el TUPA aquí...")

if user_input:
    process_user_input(user_input)
    st.rerun()

# ---------------------------
# INFORMACIÓN SUTIL AL FINAL
# ---------------------------
# Solo mostrar información adicional si no hay conversación activa
if not st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Consejos de uso sutiles
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #007bff; margin: 20px 0;'>
            <p style='margin: 0; font-size: 0.9rem; color: #666;'>
                💡 <strong>Ejemplos de consultas:</strong><br>
                • "¿Cuáles son los requisitos para licencia de funcionamiento?"<br>
                • "¿Cuánto cuesta el certificado de compatibilidad de uso?"<br>
                • "¿Cuánto tiempo demora una autorización sanitaria?"
            </p>
        </div>
    """, unsafe_allow_html=True)

# Footer sutil (siempre visible pero discreto)
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    with st.expander("ℹ️ ¿Qué es el TUPA?", expanded=False):
        st.markdown("""
        <div style='font-size: 0.9rem;'>
        El <strong>Texto Único de Procedimientos Administrativos (TUPA)</strong> contiene todos los 
        trámites del Gobierno Regional del Cusco con información sobre:
        
        📋 Requisitos necesarios  
        ⏱️ Plazos de atención  
        💰 Costos asociados  
        📜 Base legal  
        🏢 Oficinas responsables
        </div>
        """, unsafe_allow_html=True)

st.markdown(
    "<p style='text-align: center; color: #aaa; font-size: 0.8rem; margin-top: 30px;'>"
    "🏛️ Gobierno Regional del Cusco • Asistente TUPA Demo"
    "</p>", 
    unsafe_allow_html=True
)
