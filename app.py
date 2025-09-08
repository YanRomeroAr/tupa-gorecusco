import streamlit as st
import openai
import time
import re
from typing import Optional

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
st.set_page_config(
    page_title="Asistente TUPA - Gore Cusco",
    page_icon="🤖",
    layout="centered"
)

# Configuración de OpenAI desde Streamlit secrets
try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError as e:
    st.error(f"❌ Error de configuración: {e}")
    st.error("Configura las variables en Streamlit Cloud: Settings > Secrets")
    st.stop()

# ---------------------------
# ESTILOS MEJORADOS
# ---------------------------
st.markdown("""
    <style>
        /* Fondo y colores */
        .stApp { background-color: #f8f9fa; }
        
        /* Header personalizado */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .header-container h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .header-container p {
            margin: 10px 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Chat mejorado */
        .stChatMessage {
            border-radius: 15px !important;
            margin: 10px 0 !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        }
        
        /* Input mejorado */
        .stChatInputContainer {
            border-radius: 25px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
        }
        
        /* Botones */
        .stButton > button {
            border-radius: 20px;
            border: none;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* Alertas */
        .stAlert { border-radius: 10px !important; }
        
        /* Indicador de carga */
        .loading-container {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        .loading-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #2196f3;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# FUNCIONES PRINCIPALES
# ---------------------------
def init_session_state():
    """Inicializa el estado de la sesión"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

def is_contextual_query(user_input: str) -> bool:
    """Detecta si es una consulta contextual"""
    contextual_phrases = [
        "no entendí", "explica", "más claro", "repite", "aclara",
        "qué significa", "no quedó claro", "más simple", "detalla"
    ]
    return any(phrase in user_input.lower() for phrase in contextual_phrases)

def clean_response(response: str) -> str:
    """Limpia la respuesta del asistente"""
    if not response:
        return "Lo siento, no pude generar una respuesta. Intenta nuevamente."
    
    # Remover referencias de documentos
    response = re.sub(r'【\d+:.*?】', '', response)
    response = re.sub(r'\s+', ' ', response).strip()
    
    return response

def create_thread() -> Optional[str]:
    """Crea un nuevo hilo de conversación"""
    try:
        thread = openai.beta.threads.create()
        return thread.id
    except Exception as e:
        st.error(f"Error creando conversación: {e}")
        return None

def send_message(thread_id: str, content: str) -> bool:
    """Envía mensaje al asistente"""
    try:
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        return True
    except Exception as e:
        st.error(f"Error enviando mensaje: {e}")
        return False

def get_assistant_response(thread_id: str) -> Optional[str]:
    """Obtiene respuesta del asistente"""
    try:
        # Ejecutar asistente
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Esperar completación
        max_attempts = 30
        for _ in range(max_attempts):
            status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if status.status == "completed":
                break
            elif status.status == "failed":
                st.error("Error procesando respuesta")
                return None
            
            time.sleep(1)
        
        # Obtener mensajes
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        
        for msg in messages.data:
            if msg.role == "assistant":
                return clean_response(msg.content[0].text.value)
        
        return None
        
    except Exception as e:
        st.error(f"Error obteniendo respuesta: {e}")
        return None

def validate_input(user_input: str) -> tuple[bool, str]:
    """Valida la entrada del usuario"""
    if not user_input or len(user_input.strip()) == 0:
        return False, "La consulta no puede estar vacía"
    
    if len(user_input) > 1000:
        return False, "La consulta es demasiado larga (máximo 1000 caracteres)"
    
    return True, ""

def process_query(user_input: str):
    """Procesa la consulta del usuario"""
    # Validar entrada
    is_valid, error_msg = validate_input(user_input)
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return
    
    # Determinar si es contextual
    is_contextual = is_contextual_query(user_input)
    
    # Gestionar thread
    if not st.session_state.thread_id or not is_contextual:
        st.session_state.thread_id = create_thread()
        if not st.session_state.thread_id:
            return
    
    # Agregar mensaje del usuario
    st.session_state.messages.append(("usuario", user_input))
    
    # Mostrar indicador de carga
    with st.empty():
        st.markdown("""
            <div class="loading-container">
                <div class="loading-dot"></div>
                <div class="loading-dot" style="animation-delay: 0.2s;"></div>
                <div class="loading-dot" style="animation-delay: 0.4s;"></div>
                <span style="margin-left: 10px;">🤖 Generando respuesta...</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Enviar mensaje y obtener respuesta
        if send_message(st.session_state.thread_id, user_input):
            response = get_assistant_response(st.session_state.thread_id)
            
            if response:
                st.session_state.messages.append(("asistente", response))
            else:
                st.session_state.messages.append((
                    "asistente", 
                    "Lo siento, hubo un problema. Por favor, intenta nuevamente."
                ))

# ---------------------------
# INTERFAZ PRINCIPAL
# ---------------------------
init_session_state()

# Header
st.markdown("""
    <div class="header-container">
        <h1>🤖 Asistente TUPA</h1>
        <p>Gobierno Regional del Cusco</p>
        <p style="font-size: 0.9rem; margin-top: 5px;">
            Consultas sobre procedimientos administrativos
        </p>
    </div>
""", unsafe_allow_html=True)

# Mostrar mensajes
for role, message in st.session_state.messages:
    with st.chat_message("user" if role == "usuario" else "assistant"):
        st.markdown(message)

# Input del usuario
if prompt := st.chat_input("💬 Escribe tu consulta sobre el TUPA..."):
    process_query(prompt)
    st.rerun()

# Sidebar con controles
with st.sidebar:
    st.header("🛠️ Controles")
    
    if st.button("🗑️ Nueva conversación"):
        st.session_state.messages = []
        st.session_state.thread_id = None
        st.rerun()
    
    st.divider()
    
    # Estadísticas básicas
    st.metric("Mensajes", len(st.session_state.messages))
    st.metric("Conversación activa", "Sí" if st.session_state.thread_id else "No")

# Información del TUPA
with st.expander("ℹ️ ¿Qué es el TUPA?"):
    st.markdown("""
    El **Texto Único de Procedimientos Administrativos (TUPA)** contiene todos los 
    procedimientos del Gobierno Regional del Cusco:
    
    - 📝 **Requisitos** necesarios
    - ⏰ **Plazos** de atención  
    - 💰 **Costos** asociados
    - 🏢 **Ubicaciones** y horarios
    - 📚 **Base legal**
    
    ¡Pregúntame lo que necesites saber!
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>"
    "🏛️ Gobierno Regional del Cusco - Demo TUPA"
    "</p>", 
    unsafe_allow_html=True
)
