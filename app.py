import streamlit as st
import openai
import time
import re
from typing import Optional

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
st.set_page_config(
    page_title="Asistente TUPA • Gore Cusco",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuración OpenAI
try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError as e:
    st.error("⚠️ Configuración requerida. Verifica tus secrets.")
    st.stop()

# ---------------------------
# DISEÑO PROFESIONAL MEJORADO
# ---------------------------
st.markdown("""
<style>
    /* Variables de diseño profesional */
    :root {
        --primary: #1e40af;
        --primary-light: #3b82f6;
        --primary-dark: #1e3a8a;
        --secondary: #64748b;
        --accent: #0ea5e9;
        --success: #059669;
        --warning: #d97706;
        --error: #dc2626;
        --background: #ffffff;
        --surface: #f8fafc;
        --surface-2: #f1f5f9;
        --border: #e2e8f0;
        --border-strong: #cbd5e1;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --radius: 16px;
        --radius-lg: 24px;
        --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Reset completo */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', system-ui, sans-serif;
        min-height: 100vh;
    }
    
    /* Header persistente con logo e identidad */
    .main-header {
        position: sticky;
        top: 0;
        z-index: 100;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border);
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        border-radius: var(--radius);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: var(--shadow-md);
    }
    
    .logo-text h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .logo-text p {
        margin: 0;
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .header-status {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 1rem;
        background: var(--surface);
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        animation: pulse 2s infinite;
    }
    
    .status-text {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    /* Hero section mejorado */
    .hero-section {
        text-align: center;
        max-width: 800px;
        margin: 0 auto 3rem auto;
        padding: 0 2rem;
    }
    
    .hero-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 1rem 0;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    .hero-description {
        font-size: 1.125rem;
        color: var(--text-muted);
        margin: 0 0 2rem 0;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Contenedor principal del chat */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Mensajes con diseño profesional */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0 !important;
        border: none !important;
        margin: 0 !important;
        animation: fadeInUp 0.3s ease-out;
    }
    
    .stChatMessage[data-testid="user-message"] > div {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        padding: 1.25rem 1.75rem !important;
        border-radius: var(--radius-lg) var(--radius-lg) 8px var(--radius-lg) !important;
        margin-left: auto !important;
        max-width: 75% !important;
        box-shadow: var(--shadow-lg) !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        font-weight: 500 !important;
        position: relative !important;
    }
    
    .stChatMessage[data-testid="user-message"] > div::before {
        content: '';
        position: absolute;
        bottom: -8px;
        right: 16px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid var(--primary);
    }
    
    .stChatMessage[data-testid="assistant-message"] > div {
        background: white !important;
        color: var(--text-primary) !important;
        padding: 1.75rem !important;
        border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 8px !important;
        margin-right: auto !important;
        max-width: 85% !important;
        box-shadow: var(--shadow-lg) !important;
        border: 1px solid var(--border) !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
        position: relative !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] > div::before {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 16px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid white;
    }

    /* Input mejorado con borde más visible */
    .stChatInputContainer {
        background: white !important;
        border: 3px solid var(--border-strong) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-xl) !important;
        transition: var(--transition) !important;
        max-width: 900px !important;
        margin: 2rem auto !important;
        position: relative !important;
    }
    
    .stChatInputContainer::before {
        content: '';
        position: absolute;
        top: -3px;
        left: -3px;
        right: -3px;
        bottom: -3px;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        border-radius: var(--radius-lg);
        opacity: 0;
        transition: var(--transition);
        z-index: -1;
    }
    
    .stChatInputContainer:focus-within {
        border-color: transparent !important;
        transform: translateY(-2px) !important;
    }
    
    .stChatInputContainer:focus-within::before {
        opacity: 1;
    }
    
    .stChatInputContainer input {
        background: transparent !important;
        border: none !important;
        font-size: 1.1rem !important;
        padding: 1.25rem 1.75rem !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    .stChatInputContainer input::placeholder {
        color: var(--text-muted) !important;
        font-weight: 400 !important;
    }
    
    .stChatInputContainer button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        border: none !important;
        border-radius: calc(var(--radius-lg) - 4px) !important;
        padding: 1rem 1.25rem !important;
        margin: 0.5rem !important;
        transition: var(--transition) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .stChatInputContainer button:hover {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
        transform: scale(1.05) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    /* Acciones rápidas mejoradas */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .quick-action {
        background: white;
        border: 2px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem;
        cursor: pointer;
        transition: var(--transition);
        text-align: left;
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    
    .quick-action::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s ease;
    }
    
    .quick-action:hover {
        border-color: var(--primary);
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .quick-action:hover::before {
        left: 100%;
    }
    
    .quick-action-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .quick-action-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        font-size: 1rem;
    }
    
    .quick-action-desc {
        color: var(--text-secondary);
        font-size: 0.875rem;
        line-height: 1.4;
    }

    /* Estado de carga elegante */
    .loading-message {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.75rem;
        background: white;
        border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 8px;
        margin-right: auto;
        max-width: 300px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
        color: var(--text-secondary);
        font-size: 1rem;
        animation: fadeInUp 0.3s ease;
        position: relative;
    }
    
    .loading-message::before {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 16px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid white;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: var(--primary);
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }

    /* Sidebar mejorado para todos los navegadores */
    .sidebar-controls {
        position: fixed;
        top: 50%;
        right: 2rem;
        transform: translateY(-50%);
        background: white;
        border-radius: var(--radius);
        padding: 1rem;
        box-shadow: var(--shadow-xl);
        border: 1px solid var(--border);
        z-index: 50;
        min-width: 200px;
    }
    
    .sidebar-header {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .sidebar-button {
        width: 100%;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: calc(var(--radius) - 4px);
        padding: 0.75rem 1rem;
        color: var(--text-primary);
        font-weight: 500;
        cursor: pointer;
        transition: var(--transition);
        margin-bottom: 0.75rem;
        font-size: 0.875rem;
    }
    
    .sidebar-button:hover {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }
    
    .sidebar-stats {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.875rem;
    }
    
    .stat-label {
        color: var(--text-secondary);
    }
    
    .stat-value {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Footer profesional */
    .footer {
        text-align: center;
        padding: 3rem 2rem 2rem;
        margin-top: 4rem;
        border-top: 1px solid var(--border);
        background: var(--surface);
    }
    
    .footer-content {
        max-width: 600px;
        margin: 0 auto;
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Animaciones */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .header-content {
            padding: 0 1rem;
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .hero-section {
            padding: 0 1rem;
        }
        
        .chat-container {
            padding: 0 1rem;
        }
        
        .quick-actions {
            grid-template-columns: 1fr;
            margin: 0 1rem 2rem 1rem;
        }
        
        .sidebar-controls {
            position: static;
            transform: none;
            right: auto;
            margin: 2rem 1rem;
            width: calc(100% - 2rem);
        }
        
        .stChatMessage[data-testid="user-message"] > div,
        .stChatMessage[data-testid="assistant-message"] > div {
            max-width: 90% !important;
        }
    }
    
    /* Ocultar elementos de Streamlit */
    footer { display: none; }
    .css-1kyxreq { display: none; }
    .css-15zrgzn { display: none; }
    header[data-testid="stHeader"] { display: none; }
    .css-1d391kg { display: none; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# FUNCIONES PRINCIPALES
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
    except Exception:
        return None

def send_message(thread_id: str, content: str) -> bool:
    try:
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        return True
    except Exception:
        return False

def get_response(thread_id: str) -> Optional[str]:
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
                response = msg.content[0].text.value
                return re.sub(r'【\d+:.*?】', '', response).strip()
        
        return None
    except Exception:
        return None

def process_query(query: str):
    if not query.strip():
        return
        
    if not st.session_state.thread_id:
        st.session_state.thread_id = create_thread()
        if not st.session_state.thread_id:
            st.error("No se pudo iniciar la conversación")
            return
    
    st.session_state.messages.append(("user", query))
    
    # Mostrar indicador de carga
    typing_placeholder = st.empty()
    with typing_placeholder:
        st.markdown("""
            <div class="loading-message">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span>Analizando consulta...</span>
            </div>
        """, unsafe_allow_html=True)
    
    if send_message(st.session_state.thread_id, query):
        response = get_response(st.session_state.thread_id)
        typing_placeholder.empty()
        
        if response:
            st.session_state.messages.append(("assistant", response))
        else:
            st.session_state.messages.append(("assistant", "Disculpa, tengo problemas para procesar tu consulta. Por favor, intenta nuevamente."))
    else:
        typing_placeholder.empty()
        st.session_state.messages.append(("assistant", "Error de conexión. Por favor, intenta de nuevo."))

# ---------------------------
# INTERFAZ PRINCIPAL
# ---------------------------
init_session()

# Header persistente
st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-icon">🏛️</div>
                <div class="logo-text">
                    <h1>Asistente TUPA</h1>
                    <p>Gobierno Regional del Cusco</p>
                </div>
            </div>
            <div class="header-status">
                <div class="status-dot"></div>
                <span class="status-text">Sistema Activo</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Hero section (solo cuando no hay mensajes)
if not st.session_state.messages:
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">¿En qué puedo ayudarte?</h1>
            <p class="hero-subtitle">Tu asistente inteligente para procedimientos administrativos</p>
            <p class="hero-description">
                Obtén respuestas instantáneas sobre requisitos, plazos, costos y ubicaciones 
                de los trámites del TUPA del Gobierno Regional del Cusco
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Acciones rápidas
    quick_actions = [
        {
            "icon": "📄",
            "title": "Licencia de Funcionamiento", 
            "desc": "Requisitos y documentación necesaria",
            "query": "¿Qué documentos necesito para obtener una licencia de funcionamiento?"
        },
        {
            "icon": "🏗️", 
            "title": "Permisos de Construcción",
            "desc": "Plazos y procedimientos de construcción", 
            "query": "¿Cuánto tiempo demora el trámite de permiso de construcción?"
        },
        {
            "icon": "⏰",
            "title": "Horarios de Atención",
            "desc": "Ubicaciones y horarios de oficinas",
            "query": "¿Cuáles son los horarios de atención de las oficinas?"
        },
        {
            "icon": "💰",
            "title": "Tasas y Costos", 
            "desc": "Información sobre pagos y aranceles",
            "query": "¿Cuánto cuesta un certificado de zonificación?"
        }
    ]
    
    actions_html = '<div class="quick-actions">'
    for action in quick_actions:
        actions_html += f'''
            <div class="quick-action" onclick="
                const input = window.parent.document.querySelector('[data-testid=stChatInput] textarea');
                if (input) {{
                    input.value = '{action["query"]}';
                    input.focus();
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            ">
                <span class="quick-action-icon">{action["icon"]}</span>
                <div class="quick-action-title">{action["title"]}</div>
                <div class="quick-action-desc">{action["desc"]}</div>
            </div>
        '''
    actions_html += '</div>'
    
    st.markdown(actions_html, unsafe_allow_html=True)

# Contenedor del chat
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Mostrar mensajes
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(message)

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar universal (funciona en todos los navegadores)
if st.session_state.messages:
    st.markdown(f"""
        <div class="sidebar-controls">
            <div class="sidebar-header">Controles</div>
            <button class="sidebar-button" onclick="
                window.parent.postMessage({{type: 'newConversation'}}, '*');
            ">
                ↻ Nueva Conversación
            </button>
            <div class="sidebar-stats">
                <div class="stat-item">
                    <span class="stat-label">Mensajes:</span>
                    <span class="stat-value">{len(st.session_state.messages)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Estado:</span>
                    <span class="stat-value">{'🟢 Activo' if st.session_state.thread_id else '⚪ Listo'}</span>
                </div>
            </div>
        </div>
        
        <script>
            window.addEventListener('message', function(event) {{
                if (event.data.type === 'newConversation') {{
                    window.location.reload();
                }}
            }});
        </script>
    """, unsafe_allow_html=True)

# Input de chat
if prompt := st.chat_input("Escribe tu consulta sobre procedimientos del TUPA..."):
    process_query(prompt)
    st.rerun()

# Footer profesional
st.markdown("""
    <div class="footer">
        <div class="footer-content">
            <strong>🏛️ Gobierno Regional del Cusco</strong><br>
            Asistente TUPA • Facilitando el acceso a información pública<br>
            <small>Desarrollado para mejorar la atención ciudadana</small>
        </div>
    </div>
""", unsafe_allow_html=True)
