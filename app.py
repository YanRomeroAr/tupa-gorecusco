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
    layout="centered"
)

# Configuración OpenAI
try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError as e:
    st.error("⚠️ Configuración requerida. Verifica tus secrets.")
    st.stop()

# ---------------------------
# DISEÑO LIMPIO Y PROFESIONAL
# ---------------------------
st.markdown("""
<style>
    /* Variables de diseño */
    :root {
        --primary: #1e40af;
        --primary-light: #3b82f6;
        --secondary: #64748b;
        --accent: #0ea5e9;
        --success: #059669;
        --background: #ffffff;
        --surface: #f8fafc;
        --border: #e2e8f0;
        --border-focus: #3b82f6;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --radius: 16px;
        --transition: all 0.2s ease;
    }

    /* Reset */
    .stApp {
        background: var(--background);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    /* Header principal */
    .main-header {
        background: white;
        padding: 1.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(10px);
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1000px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: white;
        box-shadow: var(--shadow);
    }
    
    .logo-text h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .logo-text p {
        margin: 0;
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .status-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 24px;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    /* Hero section */
    .hero {
        text-align: center;
        max-width: 800px;
        margin: 0 auto 3rem auto;
        padding: 0 2rem;
    }
    
    .hero h1 {
        font-size: clamp(2.5rem, 5vw, 3.5rem);
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 1rem 0;
        line-height: 1.1;
    }
    
    .hero p {
        font-size: 1.125rem;
        color: var(--text-secondary);
        margin: 0 0 0.5rem 0;
        line-height: 1.6;
    }
    
    .hero .subtitle {
        font-size: 1rem;
        color: var(--text-muted);
        font-weight: 400;
    }

    /* Acciones rápidas */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem auto;
        max-width: 800px;
    }
    
    .action-card {
        background: white;
        border: 2px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        text-align: left;
        transition: var(--transition);
        cursor: pointer;
        box-shadow: var(--shadow);
    }
    
    .action-card:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .action-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .action-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .action-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.4;
    }

    /* Chat messages */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0 !important;
        border: none !important;
        margin: 0 !important;
    }
    
    .stChatMessage[data-testid="user-message"] > div {
        background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
        color: white !important;
        padding: 1.25rem 1.75rem !important;
        border-radius: 24px 24px 8px 24px !important;
        margin-left: auto !important;
        max-width: 75% !important;
        box-shadow: var(--shadow-lg) !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        font-weight: 500 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] > div {
        background: white !important;
        color: var(--text-primary) !important;
        padding: 1.75rem !important;
        border-radius: 24px 24px 24px 8px !important;
        margin-right: auto !important;
        max-width: 85% !important;
        box-shadow: var(--shadow-lg) !important;
        border: 1px solid var(--border) !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }

    /* Input mejorado */
    .stChatInputContainer {
        background: white !important;
        border: 3px solid var(--border) !important;
        border-radius: 24px !important;
        box-shadow: var(--shadow-lg) !important;
        transition: var(--transition) !important;
        margin: 2rem 0 !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1), var(--shadow-lg) !important;
        transform: translateY(-2px) !important;
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
    }
    
    .stChatInputContainer button {
        background: var(--primary) !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 1rem 1.25rem !important;
        margin: 0.5rem !important;
        transition: var(--transition) !important;
    }
    
    .stChatInputContainer button:hover {
        background: var(--primary-light) !important;
        transform: scale(1.05) !important;
    }

    /* Loading state */
    .loading {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        background: white;
        border-radius: 24px 24px 24px 8px;
        margin-right: auto;
        max-width: 300px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        color: var(--text-secondary);
    }
    
    .dots {
        display: flex;
        gap: 4px;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        background: var(--primary);
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }

    /* Sidebar */
    .sidebar-info {
        position: fixed;
        top: 50%;
        right: 2rem;
        transform: translateY(-50%);
        background: white;
        padding: 1.5rem;
        border-radius: var(--radius);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border);
        min-width: 200px;
        z-index: 50;
    }
    
    .sidebar-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stat {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        font-size: 0.875rem;
    }
    
    .stat-label {
        color: var(--text-secondary);
    }
    
    .stat-value {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Animaciones */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Responsive */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .quick-actions {
            grid-template-columns: 1fr;
            padding: 0 1rem;
        }
        
        .sidebar-info {
            position: static;
            transform: none;
            margin: 2rem auto;
            max-width: 300px;
        }
        
        .stChatMessage[data-testid="user-message"] > div,
        .stChatMessage[data-testid="assistant-message"] > div {
            max-width: 90% !important;
        }
    }
    
    /* Ocultar elementos Streamlit */
    footer { display: none; }
    header[data-testid="stHeader"] { display: none; }
    .css-1kyxreq { display: none; }
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
    
    # Indicador de carga
    typing_placeholder = st.empty()
    with typing_placeholder:
        st.markdown("""
            <div class="loading">
                <div class="dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
                <span>Procesando consulta...</span>
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
# INTERFAZ
# ---------------------------
init_session()

# Header
st.markdown("""
    <div class="main-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo">🏛️</div>
                <div class="logo-text">
                    <h1>Asistente TUPA</h1>
                    <p>Gobierno Regional del Cusco</p>
                </div>
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                <span>Sistema Activo</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Hero (solo si no hay mensajes)
if not st.session_state.messages:
    st.markdown("""
        <div class="hero">
            <h1>¿En qué puedo ayudarte?</h1>
            <p>Tu asistente inteligente para procedimientos administrativos</p>
            <p class="subtitle">
                Obtén respuestas instantáneas sobre requisitos, plazos, costos y ubicaciones 
                de los trámites del TUPA del Gobierno Regional del Cusco
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Acciones rápidas (sin JavaScript problemático)
    st.markdown("""
        <div class="quick-actions">
            <div class="action-card">
                <span class="action-icon">📄</span>
                <div class="action-title">Licencia de Funcionamiento</div>
                <div class="action-desc">Requisitos y documentación necesaria</div>
            </div>
            <div class="action-card">
                <span class="action-icon">🏗️</span>
                <div class="action-title">Permisos de Construcción</div>
                <div class="action-desc">Plazos y procedimientos de construcción</div>
            </div>
            <div class="action-card">
                <span class="action-icon">⏰</span>
                <div class="action-title">Horarios de Atención</div>
                <div class="action-desc">Ubicaciones y horarios de oficinas</div>
            </div>
            <div class="action-card">
                <span class="action-icon">💰</span>
                <div class="action-title">Tasas y Costos</div>
                <div class="action-desc">Información sobre pagos y aranceles</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Mostrar mensajes
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(message)

# Sidebar simple (sin JavaScript)
if st.session_state.messages:
    st.markdown(f"""
        <div class="sidebar-info">
            <div class="sidebar-title">Estado</div>
            <div class="stat">
                <span class="stat-label">Mensajes:</span>
                <span class="stat-value">{len(st.session_state.messages)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Conversación:</span>
                <span class="stat-value">{'🟢 Activa' if st.session_state.thread_id else '⚪ Lista'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Input principal
if prompt := st.chat_input("Escribe tu consulta sobre procedimientos del TUPA..."):
    process_query(prompt)
    st.rerun()

# Sidebar de Streamlit para nueva conversación
with st.sidebar:
    st.header("🛠️ Controles")
    if st.button("🔄 Nueva Conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = None
        st.rerun()
    
    if st.session_state.messages:
        st.divider()
        st.metric("Mensajes", len(st.session_state.messages))
        st.metric("Estado", "🟢 Activo" if st.session_state.thread_id else "⚪ Listo")

# Footer
if st.session_state.messages:
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; padding: 2rem; color: #64748b;'>"
        "🏛️ <strong>Gobierno Regional del Cusco</strong> • Asistente TUPA<br>"
        "<small>Facilitando el acceso a información pública</small>"
        "</div>", 
        unsafe_allow_html=True
    )
