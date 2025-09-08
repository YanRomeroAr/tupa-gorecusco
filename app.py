import streamlit as st
import openai
import time
import re
from typing import Optional

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
st.set_page_config(
    page_title="TUPA Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# OpenAI Configuration
try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError as e:
    st.error("⚠️ Configuration required. Please check your secrets.")
    st.stop()

# ---------------------------
# DISEÑO PROFESIONAL MINIMALISTA
# ---------------------------
st.markdown("""
<style>
    /* Reset y variables CSS */
    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --secondary-color: #64748b;
        --success-color: #059669;
        --background: #ffffff;
        --surface: #f8fafc;
        --border: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --radius: 12px;
        --radius-sm: 8px;
        --spacing: 1rem;
    }

    /* Layout base ultra limpio */
    .stApp {
        background: var(--background);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    }
    
    /* Header minimalista */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem 3rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 1rem 0;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin: 0 0 0.5rem 0;
        font-weight: 400;
    }
    
    .hero-description {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin: 0;
        font-weight: 300;
        opacity: 0.8;
    }

    /* Chat container profesional */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Messages con diseño Apple-style */
    .stChatMessage {
        background: transparent !important;
        padding: 1.5rem 0 !important;
        border: none !important;
        margin: 0 !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: transparent !important;
    }
    
    .stChatMessage[data-testid="user-message"] > div {
        background: var(--primary-color) !important;
        color: white !important;
        padding: 1rem 1.5rem !important;
        border-radius: 18px 18px 4px 18px !important;
        margin-left: auto !important;
        max-width: 70% !important;
        box-shadow: var(--shadow-sm) !important;
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] > div {
        background: var(--surface) !important;
        color: var(--text-primary) !important;
        padding: 1.5rem !important;
        border-radius: 18px 18px 18px 4px !important;
        margin-right: auto !important;
        max-width: 85% !important;
        box-shadow: var(--shadow-sm) !important;
        border: 1px solid var(--border) !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    /* Input ultra profesional */
    .stChatInputContainer {
        background: white !important;
        border: 2px solid var(--border) !important;
        border-radius: 24px !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.2s ease !important;
        max-width: 800px !important;
        margin: 2rem auto !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1), var(--shadow-lg) !important;
    }
    
    .stChatInputContainer input {
        background: transparent !important;
        border: none !important;
        font-size: 1rem !important;
        padding: 1rem 1.5rem !important;
        color: var(--text-primary) !important;
    }
    
    .stChatInputContainer input::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7 !important;
    }
    
    .stChatInputContainer button {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInputContainer button:hover {
        background: var(--primary-hover) !important;
        transform: scale(1.05) !important;
    }

    /* Status indicator minimalista */
    .status-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--surface);
        z-index: 1000;
        border-bottom: 1px solid var(--border);
    }
    
    .status-active {
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--success-color));
        width: 100%;
        animation: pulse 2s infinite;
    }

    /* Loading state elegante */
    .loading-message {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1.5rem;
        background: var(--surface);
        border-radius: 18px 18px 18px 4px;
        margin-right: auto;
        max-width: 200px;
        border: 1px solid var(--border);
        color: var(--text-secondary);
        font-size: 0.9rem;
        animation: fadeIn 0.3s ease;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dot {
        width: 6px;
        height: 6px;
        background: var(--text-secondary);
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }

    /* Quick actions minimalista */
    .quick-actions {
        display: flex;
        gap: 0.75rem;
        justify-content: center;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .quick-action {
        background: white;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 0.75rem 1.25rem;
        font-size: 0.9rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
    }
    
    .quick-action:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        text-decoration: none;
    }

    /* Animaciones suaves */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }

    /* Sidebar minimalista */
    .css-1d391kg { padding-top: 2rem; }
    
    /* Footer ultra limpio */
    .footer {
        text-align: center;
        padding: 3rem 2rem 2rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
        border-top: 1px solid var(--border);
        margin-top: 4rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-section {
            padding: 2rem 1rem;
        }
        
        .chat-container {
            padding: 0 1rem;
        }
        
        .stChatMessage[data-testid="user-message"] > div,
        .stChatMessage[data-testid="assistant-message"] > div {
            max-width: 90% !important;
        }
        
        .quick-actions {
            flex-direction: column;
            align-items: center;
        }
        
        .quick-action {
            width: 100%;
            max-width: 300px;
            text-align: center;
        }
    }
    
    /* Ocultar elementos innecesarios */
    .css-1kyxreq { display: none; }
    footer { display: none; }
    .css-15zrgzn { display: none; }
    header[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# FUNCIONES CORE
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
            st.error("Unable to start conversation")
            return
    
    st.session_state.messages.append(("user", query))
    
    # Show typing indicator
    typing_placeholder = st.empty()
    with typing_placeholder:
        st.markdown("""
            <div class="loading-message">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span>Thinking...</span>
            </div>
        """, unsafe_allow_html=True)
    
    if send_message(st.session_state.thread_id, query):
        response = get_response(st.session_state.thread_id)
        typing_placeholder.empty()
        
        if response:
            st.session_state.messages.append(("assistant", response))
        else:
            st.session_state.messages.append(("assistant", "I apologize, but I'm having trouble processing your request. Please try again."))
    else:
        typing_placeholder.empty()
        st.session_state.messages.append(("assistant", "Connection error. Please try again."))

# ---------------------------
# UI PRINCIPAL
# ---------------------------
init_session()

# Status bar
st.markdown('<div class="status-bar"><div class="status-active"></div></div>', unsafe_allow_html=True)

# Hero section
if not st.session_state.messages:
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">TUPA Assistant</h1>
            <p class="hero-subtitle">Gobierno Regional del Cusco</p>
            <p class="hero-description">
                Get instant answers about administrative procedures, requirements, and regulations
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("""
        <div class="quick-actions">
            <div class="quick-action" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='What documents do I need for a business license?'; document.querySelector('[data-testid=stChatInput] textarea').focus();">📄 Business License</div>
            <div class="quick-action" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='How long does construction permit take?'; document.querySelector('[data-testid=stChatInput] textarea').focus();">🏗️ Construction Permits</div>
            <div class="quick-action" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='What are the office hours?'; document.querySelector('[data-testid=stChatInput] textarea').focus();">⏰ Office Hours</div>
            <div class="quick-action" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='How much does a zoning certificate cost?'; document.querySelector('[data-testid=stChatInput] textarea').focus();">💰 Fees & Costs</div>
        </div>
    """, unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(message)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask about TUPA procedures..."):
    process_query(prompt)
    st.rerun()

# Minimal sidebar
with st.sidebar:
    if st.session_state.messages:
        if st.button("↻ New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = None
            st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    st.markdown(f"**Status:** {'🟢 Active' if st.session_state.thread_id else '⚪ Ready'}")

# Footer
if st.session_state.messages:
    st.markdown("""
        <div class="footer">
            🏛️ Gobierno Regional del Cusco • TUPA Assistant
        </div>
    """, unsafe_allow_html=True)
