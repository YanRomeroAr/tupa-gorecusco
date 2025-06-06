import streamlit as st
import openai
import time
import re

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
# Configuración de OpenAI
try:
    openai.api_key = st.secrets["openai_api_key"]
    assistant_id = st.secrets["assistant_id"]
except KeyError as e:
    st.error(f"Error de configuración: Falta {e} en los secretos")
    st.stop()

# ---------------------------
# ESTILOS PERSONALIZADOS
# ---------------------------
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

# ---------------------------
# HEADER CON LOGO Y TÍTULO
# ---------------------------
st.markdown(f"""
    <div class="header-container">
        <div class="header-logo">
            <img src="https://goresedetramitedigital.regioncusco.gob.pe/filest/images/logoRegion.png" width="120" alt="Logo Gore Cusco">
        </div>
        <div class="header-text">
            <h1>Demo - Bot del TUPA Gore Cusco</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1rem; color: #666;">
                Haz tus consultas sobre el Texto Único de Procedimientos Administrativos (TUPA) del Gobierno Regional del Cusco y obtén respuestas claras, rápidas y confiables sobre requisitos, plazos y costos de cada trámite.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------
# INICIALIZACIÓN DE ESTADO
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "historial_preguntas" not in st.session_state:
    st.session_state.historial_preguntas = []

# ---------------------------
# MOSTRAR HISTORIAL DE CHAT
# ---------------------------
for role, message in st.session_state.messages:
    with st.chat_message("user" if role == "usuario" else "assistant"):
        st.markdown(message)

# ---------------------------
# PROCESAMIENTO DE ENTRADA
# ---------------------------
user_input = st.chat_input("💬 Escribe tu consulta sobre el TUPA aquí...")

if user_input:
    # Palabras clave contextuales
    frases_contextuales = [
        "no entendí", "explica", "dudas", "más claro", "más simple", "no me parece",
        "repite", "aclara", "sencillo", "para qué sirve", "cuál es el objetivo", 
        "qué finalidad tiene", "por qué se hace", "qué implica", "cuál es el propósito",
        "a qué se refiere", "qué significa esto", "no quedó claro", "detalla mejor",
        "en otras palabras", "hazlo más fácil", "explícame mejor", "no me queda claro"
    ]
    
    es_contextual = any(frase in user_input.lower() for frase in frases_contextuales)
    
    # Preparar prompt
    if es_contextual and st.session_state.historial_preguntas and st.session_state.thread_id:
        referencia = st.session_state.historial_preguntas[-1]
        prompt = f"Responde con más claridad sobre esto: {referencia}. Pregunta actual: {user_input}"
    else:
        prompt = user_input
        if not es_contextual:
            # Crear nuevo hilo para consultas no contextuales
            thread = openai.beta.threads.create()
            st.session_state.thread_id = thread.id
            st.session_state.historial_preguntas.append(user_input)
    
    # Agregar mensaje del usuario al chat
    st.session_state.messages.append(("usuario", user_input))
    
    try:
        # Enviar mensaje al asistente
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        
        # Ejecutar asistente
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
        )
        
        # Esperar respuesta con spinner
        with st.spinner("🤖 Generando respuesta..."):
            max_attempts = 60
            attempts = 0
            
            while attempts < max_attempts:
                status_info = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                
                if status_info.status == "completed":
                    break
                elif status_info.status == "failed":
                    st.error("Error al procesar la respuesta del asistente")
                    break
                
                time.sleep(1)
                attempts += 1
            
            if attempts < max_attempts and status_info.status == "completed":
                # Obtener respuesta
                messages = openai.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                
                for msg in messages.data:
                    if msg.role == "assistant":
                        # Limpiar respuesta
                        respuesta = re.sub(r'【\d+:.*?†.*?】', '', msg.content[0].text.value)
                        st.session_state.messages.append(("asistente", respuesta))
                        break
            else:
                st.session_state.messages.append(("asistente", "Lo siento, hubo un error al procesar tu consulta. Por favor, intenta nuevamente."))
    
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.session_state.messages.append(("asistente", "Error de conexión. Por favor, intenta nuevamente."))

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
